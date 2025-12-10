
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool

tools_to_delete = ['Group Chat', 'PDF to Word']
deleted_count, _ = Tool.objects.filter(name__in=tools_to_delete).delete()

print(f"Deleted {deleted_count} tools: {tools_to_delete}")
