from django.contrib import admin
from .models import PageSession, ButtonClick


@admin.register(PageSession)
class PageSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'loaded_at', 'country_name', 'ip_address', 'clicked', 'time_to_click')
    list_filter = ('clicked', 'loaded_at', 'country_name')
    search_fields = ('session_id', 'ip_address', 'country_name')
    readonly_fields = ('session_id', 'loaded_at')


@admin.register(ButtonClick)
class ButtonClickAdmin(admin.ModelAdmin):
    list_display = ('session', 'clicked_at', 'time_elapsed')
    list_filter = ('clicked_at',)
    readonly_fields = ('session', 'clicked_at', 'time_elapsed')
