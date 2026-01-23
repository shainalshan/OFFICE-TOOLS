from django.db import models

from django.contrib.auth.models import User

class KnowledgeBaseItem(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, help_text="Direct text content for the AI to learn.")
    file = models.FileField(upload_to='knowledge_base/', blank=True, null=True, help_text="Upload text or PDF files.")
    
    # Ownership Scoping
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_global = models.BooleanField(default=False, help_text="If True, accessible by everyone (Admin memory).")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class AIFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    query = models.TextField()
    response = models.TextField()
    rating = models.IntegerField(choices=[(1, 'Thumbs Up'), (-1, 'Thumbs Down')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.rating} - {self.created_at}"
