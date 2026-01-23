import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Tool, UserToolAccess
from django.contrib.auth.models import User

def setup_tool():
    tool_name = "File Converter"
    tool_slug = "converter"
    tool_desc = "Convert and compress PDF, Excel, and Image files."
    
    tool, created = Tool.objects.get_or_create(
        slug=tool_slug,
        defaults={'name': tool_name, 'description': tool_desc, 'is_active': True}
    )
    
    if created:
        print(f"Created tool: {tool_name}")
    else:
        print(f"Tool already exists: {tool_name}")
        
    # Grant access to all superusers
    superusers = User.objects.filter(is_superuser=True)
    for user in superusers:
        access, _ = UserToolAccess.objects.get_or_create(user=user)
        access.tools.add(tool)
        print(f"Granted access to {user.username}")

if __name__ == "__main__":
    setup_tool()
