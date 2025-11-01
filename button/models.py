from django.db import models
from django.utils import timezone
import uuid


class PageSession(models.Model):
    """Track each page visit/session"""
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loaded_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    clicked = models.BooleanField(default=False)
    time_to_click = models.FloatField(null=True, blank=True, help_text="Seconds from page load to click")

    class Meta:
        ordering = ['-loaded_at']

    def __str__(self):
        return f"Session {self.session_id} - {'Clicked' if self.clicked else 'Not clicked'}"


class ButtonClick(models.Model):
    """Record each button click with timestamp"""
    session = models.ForeignKey(PageSession, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(default=timezone.now)
    time_elapsed = models.FloatField(help_text="Seconds from page load to click")

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click from session {self.session.session_id} at {self.clicked_at}"
