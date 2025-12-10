from django.db import models
from django.conf import settings

class RequestLog(models.Model):
    path = models.CharField(max_length=1024)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    response_time = models.FloatField(help_text="Response time in seconds")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.path} ({self.status_code})"

class ErrorLog(models.Model):
    message = models.TextField()
    traceback = models.TextField()
    path = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Error: {self.message[:50]}..."
