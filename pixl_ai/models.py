from django.db import models
from django.conf import settings

class AI_KnowledgeBase(models.Model):
    ACCESS_LEVEL_CHOICES = [
        ('H1', 'H1 - Admin Only'),
        ('H2', 'H2 - Employees'),
        ('H3', 'H3 - Guests/Basic'),
    ]

    topic = models.CharField(max_length=255)
    content = models.TextField()
    access_level = models.CharField(max_length=2, choices=ACCESS_LEVEL_CHOICES, default='H3')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.topic} ({self.access_level})"

class Chat_Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user} at {self.timestamp}"
