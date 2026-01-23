
import os
import django
from django.conf import settings
from django.template import Template, Context, Engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'backup_restore/templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.staticfiles',
            'backup_restore', # Mock app name or just rely on file loading
        ]
    )
    django.setup()

def check_template():
    file_path = os.path.join(BASE_DIR, 'backup_restore/templates/backup_restore/dashboard_v4.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Checking {file_path}...")
    try:
        # We use a raw engine to avoid dependency issues with extending 'core/base.html' if not found
        # But wait, extends will fail if it can't find base.
        # So we better just try to compile the string.
        # But 'extends' tag will be processed.
        # If we just want to check syntax of THIS file, we might have issues if it tries to load parent.
        # Let's try to just parsing it.
        
        t = Template(content)
        print("Template syntax is VALID.")
    except Exception as e:
        print("Template syntax ERROR:")
        print(e)

if __name__ == '__main__':
    check_template()
