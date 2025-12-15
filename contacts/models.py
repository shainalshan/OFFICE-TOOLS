from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    staff_no = models.CharField(max_length=50, blank=True, null=True)
    personal_devices = models.TextField(blank=True, null=True, help_text="Count or details of personal devices")
    designation = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True) # Keeping as CharField for flexibility (extensions etc)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"
