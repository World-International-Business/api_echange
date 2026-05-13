import hashlib
import secrets
from django.db import models
from django.contrib.auth.models import User


class APIClient(models.Model):
    TIER_CHOICES = [
        ('free', 'Free'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('partner', 'Partner'),
    ]
    QUOTA_MAP = {
        'free': 100,
        'standard': 1000,
        'premium': 5000,
        'partner': 50000,
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_clients')
    name = models.CharField(max_length=100)
    api_key_prefix = models.CharField(max_length=8)
    api_key_hash = models.CharField(max_length=64, unique=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    quota_requests_per_hour = models.PositiveIntegerField(default=100)
    total_requests = models.PositiveBigIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tier}) - {self.api_key_prefix}..."

    @classmethod
    def generate_key(cls):
        raw_key = f"fxp_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        prefix = raw_key[:8]
        return raw_key, key_hash, prefix

    @classmethod
    def verify_key(cls, raw_key):
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            return cls.objects.get(api_key_hash=key_hash, is_active=True)
        except cls.DoesNotExist:
            return None


class AuditLog(models.Model):
    api_client = models.ForeignKey(APIClient, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField()
    ip_address = models.GenericIPAddressField(null=True)
    response_time_ms = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code}"
