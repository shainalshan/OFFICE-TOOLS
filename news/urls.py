from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('manage/', views.manage_news, name='manage_news'),
    path('api/latest/', views.get_latest_news, name='get_latest_news'),
    path('api/reminders/', views.check_reminders, name='check_reminders'),
    path('api/messages/', views.get_messages, name='get_messages'),
]
