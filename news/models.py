from django.db import models
from django.contrib.auth.models import User

class NewsItem(models.Model):
    TYPE_CHOICES = [
        ('NEWS', 'News'),
        ('EVENT', 'Event'),
        ('NOTIFICATION', 'Notification'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='NEWS')
    attachment = models.FileField(upload_to='news_attachments/', blank=True, null=True)
    reminder_datetime = models.DateTimeField(null=True, blank=True)

    @property
    def is_image(self):
        if not self.attachment:
            return False
        ext = self.attachment.name.split('.')[-1].lower()
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
