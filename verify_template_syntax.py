import os
import sys
import django

# Add project root to path
sys.path.append(r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except Exception as e:
    print(f"Setup failed: {e}")
    sys.exit(1)

from django.template.loader import get_template

print("Attempting to load template 'backup_restore/dashboard_v3.html'...")

try:
    # This will parse the template and raise TemplateSyntaxError if syntax is invalid
    template = get_template('backup_restore/dashboard_v3.html')
    print("SUCCESS: Template loaded successfully! Syntax is correct.")
    # Attempt to access the nodelist to ensure deep parsing
    print(f"Template Nodelist length: {len(template.template.nodelist)}")
except Exception as e:
    print(f"FAILURE: Template syntax error detected.")
    print(str(e))
