from django import forms
from .models import NewsItem

class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ['title', 'content', 'type', 'attachment', 'is_active', 'reminder_datetime']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
