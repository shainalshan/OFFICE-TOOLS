
import os
import django
from django.conf import settings
from django.template import Engine, TemplateSyntaxError

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.getcwd(), 'tickets', 'templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'waffle', # Needed for {% load waffle_tags %}
            'tickets',
        ],
    )
    django.setup()

def check_template(path):
    print(f"Checking {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # specific check for the known bad pattern
        if "=='" in content or "==" in content:
            # Check specifically for the syntax causing the error
            import re
            bad_pattern = re.search(r"status=='[A-Z_]+'", content)
            if bad_pattern:
                print(f"❌ FOUND BAD PATTERN ON DISK: {bad_pattern.group(0)}")
            else:
                print("✅ specific bad pattern 'status==' not found in text (good).")

        # Try to parse it with Django engine
        # We use from_string to avoid dependency on full file loading context if possible, 
        # but better to use the engine to parse the file content directly.
        engine = Engine.get_default()
        template = engine.from_string(content)
        print(f"✅ Template syntax is VALID.")
        
    except TemplateSyntaxError as e:
        print(f"❌ TemplateSyntaxError: {e}")
    except Exception as e:
        print(f"❌ Other Error: {e}")

if __name__ == "__main__":
    check_template(r"tickets\templates\tickets\ticket_detail.html")
