from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    file_type = models.CharField(max_length=50, blank=True) # e.g. 'pdf', 'docx'
    file_size = models.PositiveIntegerField(default=0) # in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # Get extension
            filename = self.file.name
            ext = os.path.splitext(filename)[1].lower().replace('.', '')
            self.file_type = ext
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
