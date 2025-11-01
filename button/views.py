from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Q, Max, Min, Sum
from urllib.parse import urlparse
from .models import PageSession, ButtonClick
import json
import requests
from datetime import timedelta
from django.utils import timezone
import IP2Location
import os
from django.conf import settings


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Initialize IP2Location database
IP2LOC_DATABASE = None
def get_ip2location_db():
    """Get or initialize IP2Location database"""
    global IP2LOC_DATABASE
    if IP2LOC_DATABASE is None:
        # Look for any BIN file in the project root
        import glob
        bin_files = glob.glob(os.path.join(settings.BASE_DIR, '*.BIN'))
        if bin_files:
            db_path = bin_files[0]  # Use the first BIN file found
            IP2LOC_DATABASE = IP2Location.IP2Location(db_path)
    return IP2LOC_DATABASE


def get_country_from_ip(ip):
    """Get country information from IP address using local IP2Location database"""
    # Skip invalid IPs
    if not ip or ip in ['127.0.0.1', 'localhost', '::1']:
        return {'country_code': '', 'country_name': ''}

    try:
        # Try local IP2Location database first
        db = get_ip2location_db()
        if db:
            rec = db.get_all(ip)
            if rec and rec.country_short and rec.country_short != '-':
                return {
                    'country_code': rec.country_short,
                    'country_name': rec.country_long
                }
    except Exception as e:
        # Log error but continue to fallback
        import logging
        logging.error(f"IP2Location error for IP {ip}: {e}")

    # Fallback to ip-api.com if local database fails
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country_code': data.get('countryCode', ''),
                    'country_name': data.get('country', '')
                }
    except Exception as e:
        import logging
        logging.error(f"ip-api error for IP {ip}: {e}")

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
    referrer = request.META.get('HTTP_REFERER', '')

    # Debug logging
    import logging
    logging.info(f"New session - IP: {ip}, X-Forwarded-For: {request.META.get('HTTP_X_FORWARDED_FOR', 'None')}")

    # Get browser info from request body
    browser_name = ''
    browser_version = ''
    try:
        data = json.loads(request.body) if request.body else {}
        browser_name = data.get('browser_name', '')
        browser_version = data.get('browser_version', '')
    except:
        pass

    # Get country info
    country_info = get_country_from_ip(ip)

    session = PageSession.objects.create(
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
        browser_name=browser_name,
        browser_version=browser_version,
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


@csrf_exempt
@require_http_methods(["POST"])
def record_reclick(request):
    """Record a reclick attempt"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        session = PageSession.objects.get(session_id=session_id)
        session.reclick_attempts += 1
        session.save()

        return JsonResponse({'status': 'success', 'reclick_attempts': session.reclick_attempts})
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
        clicks=Count('session_id'),
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

    # Total reclick attempts
    total_reclicks = PageSession.objects.aggregate(
        total=Sum('reclick_attempts')
    )['total'] or 0

    # Top referring sites
    referrer_stats = []
    sessions_with_referrer = PageSession.objects.exclude(referrer='').exclude(referrer__isnull=True)

    # Group by domain
    referrer_domains = {}
    for session in sessions_with_referrer:
        try:
            parsed = urlparse(session.referrer)
            domain = parsed.netloc or parsed.path.split('/')[0]
            if domain:
                # Clean up domain (remove www.)
                domain = domain.replace('www.', '')
                # Skip self-referrers
                if domain == 'justabutton.org':
                    continue
                if domain not in referrer_domains:
                    referrer_domains[domain] = 0
                referrer_domains[domain] += 1
        except:
            pass

    # Sort and get top 10
    referrer_stats = [
        {'domain': domain, 'visits': count}
        for domain, count in sorted(referrer_domains.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Browser statistics
    browser_stats = PageSession.objects.exclude(
        browser_name=''
    ).values('browser_name').annotate(
        count=Count('session_id')
    ).order_by('-count')[:10]

    # New statistics for symmetry
    # 1. Sessions today
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sessions_today = PageSession.objects.filter(loaded_at__gte=today_start).count()

    # 2. Clicks today
    clicks_today = ButtonClick.objects.filter(clicked_at__gte=today_start).count()

    # 3. Most active country (country with most clicks)
    most_active_country = ''
    if country_stats:
        most_active_country = country_stats[0]['country_name']

    # 4. Most popular browser
    most_popular_browser = ''
    if browser_stats:
        most_popular_browser = browser_stats[0]['browser_name']

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
        'recent_clicks': recent_list,
        'total_reclick_attempts': total_reclicks,
        'top_referrers': referrer_stats,
        'browser_stats': list(browser_stats),
        'sessions_today': sessions_today,
        'clicks_today': clicks_today,
        'most_active_country': most_active_country,
        'most_popular_browser': most_popular_browser
    })
