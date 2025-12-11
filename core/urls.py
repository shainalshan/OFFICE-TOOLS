from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('check-pending-users/', views.check_pending_users, name='check_pending_users'),
    path('news/', views.office_news, name='office_news'),
    path('chat/', views.group_chat, name='group_chat'),
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('api/notifications/search-users/', views.search_users_notification, name='search_users_notification'),
    path('api/notifications/list/', views.list_notifications, name='list_notifications'),
    path('api/notifications/check/', views.check_notifications, name='check_notifications'),
]
