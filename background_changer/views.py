
from django.shortcuts import render
from django.conf import settings
from core.decorators import check_tool_access

@check_tool_access('background-changer')
def index(request):
    # Pass the URL of the background template to the frontend
    # Assuming MEDIA_URL is /media/
    context = {
        'bg_template_url': settings.MEDIA_URL + 'background_changer/template.png'
    }
    return render(request, 'background_changer/tool.html', context)
