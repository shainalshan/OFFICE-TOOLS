import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tool

def create_test_user():
    if not User.objects.filter(username='browser_test').exists():
        user = User.objects.create_user('browser_test', 'test@example.com', 'password123')
        user.is_active = True
        user.save()
        print("User 'browser_test' created.")
        
        # Give access to News tool
        try:
            news_tool = Tool.objects.get(slug='news')
            user.tool_access.tools.add(news_tool)
        except:
            print("News tool not assignment skipped (maybe open to all or tool missing)")
    else:
        print("User 'browser_test' already exists.")

if __name__ == '__main__':
    create_test_user()
