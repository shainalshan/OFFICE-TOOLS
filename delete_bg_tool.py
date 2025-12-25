
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool

def delete_tool():
    try:
        tool = Tool.objects.get(slug='background-changer')
        print(f"Found tool: {tool.name} (ID: {tool.id})")
        tool.delete()
        print("Successfully deleted 'background-changer' tool.")
    except Tool.DoesNotExist:
        print("Tool 'background-changer' does not exist.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    delete_tool()
