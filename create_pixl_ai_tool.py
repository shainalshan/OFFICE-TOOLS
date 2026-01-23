import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool

def create_pixl_ai_tool():
    tool, created = Tool.objects.get_or_create(
        slug='pixl_ai',
        defaults={
            'name': 'Pixl AI',
            'description': 'AI Assistant & Tools',
            'is_active': True 
        }
    )
    if created:
        print("Successfully created 'Pixl AI' tool.")
    else:
        print("'Pixl AI' tool already exists.")

if __name__ == '__main__':
    create_pixl_ai_tool()
