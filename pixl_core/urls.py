from django.urls import path
from . import views

urlpatterns = [
    path('ask', views.ask_ai, name='ask_ai'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('', views.ai_chat, name='ai_home'),

    path('chat/feedback/', views.submit_ai_feedback, name='submit_ai_feedback'),
    path('restart_ai/', views.restart_ai_engine, name='restart_ai_engine'),
    path('knowledge/', views.knowledge_list, name='knowledge_list'),
    path('knowledge/add/', views.knowledge_add, name='knowledge_add'),
    path('knowledge/<int:pk>/edit/', views.knowledge_edit, name='knowledge_edit'),
    path('knowledge/<int:pk>/delete/', views.knowledge_delete, name='knowledge_delete'),
]
