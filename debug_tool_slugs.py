import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool

print("--- Current Database Tools ---")
for t in Tool.objects.all():
    print(f"Name: {t.name} | Slug: '{t.slug}' | Active: {t.is_active}")
