from django import forms
from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 50 * 1024 # 50 KB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 50 KB.')

class SignatureForm(forms.Form):
    photo = forms.ImageField(validators=[validate_file_size], required=True)
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    designation = forms.CharField(max_length=100, required=True, label="Designation")
    email = forms.EmailField(required=True, label="Email ID")
    phone = forms.CharField(max_length=20, required=True, label="Phone Number")
