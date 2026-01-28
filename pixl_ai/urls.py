from django.urls import path
from . import views
from django.shortcuts import render

def index(request):
    return render(request, 'pixl_ai/index.html')

urlpatterns = [
    path('', index, name='pixl_ai_home'),
    path('chat/', views.chat_view, name='pixl_ai_chat'),
    path('manage/', views.manage_knowledge_view, name='knowledge_list'), # Placeholder
    path('restart/', views.manage_knowledge_view, name='restart_ai_engine'), # Placeholder
    path('feedback/', views.manage_knowledge_view, name='submit_ai_feedback'), # Placeholder
    path('ask/', views.chat_view, name='ask_ai'), # Aliasing for template compatibility
]
