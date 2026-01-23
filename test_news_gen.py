import os
import django
import time
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from news.models import NewsItem
from django.contrib.auth.models import User

def generate_news():
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found.")
        return

    count = 1
    while True:
        title = f"Auto Update {count}"
        content = f"This is an automated news update generated at {timezone.now().strftime('%H:%M:%S')}."
        
        item = NewsItem.objects.create(
            title=title,
            content=content,
            created_by=user,
            type='NEWS'
        )
        print(f"Created: {title}")
        count += 1
        time.sleep(5) # Create every 5 seconds

if __name__ == '__main__':
    generate_news()
