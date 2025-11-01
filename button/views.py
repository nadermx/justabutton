from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Q, Max, Min
from .models import PageSession, ButtonClick
import json
import requests
from datetime import timedelta
from django.utils import timezone


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_from_ip(ip):
    """Get country information from IP address"""
    try:
        # Using ip-api.com (free, no key needed)
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country_code': data.get('countryCode', ''),
                    'country_name': data.get('country', '')
                }
    except:
        pass
    return {'country_code': '', 'country_name': ''}


def index(request):
    """Main page view"""
    return render(request, 'button/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """Create a new page session"""
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Get country info
    country_info = get_country_from_ip(ip)

    session = PageSession.objects.create(
        ip_address=ip,
        user_agent=user_agent,
        country_code=country_info['country_code'],
        country_name=country_info['country_name']
    )

    return JsonResponse({
        'session_id': str(session.session_id),
        'country_code': session.country_code,
        'country_name': session.country_name
    })


@csrf_exempt
@require_http_methods(["POST"])
def record_click(request):
    """Record a button click"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        time_elapsed = data.get('time_elapsed')

        session = PageSession.objects.get(session_id=session_id)
        session.clicked = True
        session.time_to_click = time_elapsed
        session.save()

        ButtonClick.objects.create(
            session=session,
            time_elapsed=time_elapsed
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def get_stats(request):
    """Get aggregated statistics"""
    total_sessions = PageSession.objects.count()
    total_clicks = ButtonClick.objects.count()
    clicked_sessions = PageSession.objects.filter(clicked=True).count()

    # Calculate click-through rate
    ctr = (clicked_sessions / total_sessions * 100) if total_sessions > 0 else 0

    # Average time to click
    avg_time = PageSession.objects.filter(clicked=True).aggregate(
        avg=Avg('time_to_click')
    )['avg'] or 0

    # Fastest and slowest clicks
    fastest = PageSession.objects.filter(clicked=True).aggregate(
        min=Min('time_to_click')
    )['min']

    slowest = PageSession.objects.filter(clicked=True).aggregate(
        max=Max('time_to_click')
    )['max']

    # Country statistics
    country_stats = PageSession.objects.filter(
        clicked=True,
        country_name__isnull=False
    ).exclude(
        country_name=''
    ).values('country_name', 'country_code').annotate(
        clicks=Count('id'),
        avg_time=Avg('time_to_click')
    ).order_by('-clicks')

    # Recent clicks (last 10)
    recent_clicks = ButtonClick.objects.select_related('session').order_by('-clicked_at')[:10]
    recent_list = [{
        'country': click.session.country_name or 'Unknown',
        'country_code': click.session.country_code or '',
        'time_elapsed': round(click.time_elapsed, 2),
        'clicked_at': click.clicked_at.isoformat()
    } for click in recent_clicks]

    return JsonResponse({
        'total_sessions': total_sessions,
        'total_clicks': total_clicks,
        'clicked_sessions': clicked_sessions,
        'bounce_rate': round(100 - ctr, 2),
        'click_through_rate': round(ctr, 2),
        'avg_time_to_click': round(avg_time, 2) if avg_time else 0,
        'fastest_click': round(fastest, 2) if fastest else None,
        'slowest_click': round(slowest, 2) if slowest else None,
        'country_stats': list(country_stats),
        'recent_clicks': recent_list
    })
