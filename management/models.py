from django.db import models
from django.conf import settings
from temples.models import Temple

class SystemAnnouncement(models.Model):
    """Requirement I.6: System-wide announcements for all pilgrims"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class ActivityLog(models.Model):
    """Requirement J.5/E.6: Entry time logs and admin actions"""
    ACTION_CHOICES = [
        ('QR_SCAN', 'QR Code Validated'),
        ('SOS_RESOLVE', 'SOS Alert Resolved'),
        ('SLOT_UPDATE', 'Slot Capacity Modified'),
    ]
    
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user.email} - {self.action_type} at {self.timestamp}"

class AdminProfile(models.Model):
    """Extends admin info for specific temple management"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_temple = models.ForeignKey(Temple, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Staff: {self.user.email}"