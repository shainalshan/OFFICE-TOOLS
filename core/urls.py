from django.urls import path
from . import views
from tickets import views as ticket_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tickets/manage-access/', ticket_views.manage_ticket_access, name='manage_ticket_access'),
    path('tickets/manage-assignees/', ticket_views.manage_ticket_assignees, name='manage_ticket_assignees'),
    path('check-pending-users/', views.check_pending_users, name='check_pending_users'),
    path('news/', views.office_news, name='office_news'),
    path('chat/', views.group_chat, name='group_chat'),
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('api/notifications/search-users/', views.search_users_notification, name='search_users_notification'),
    path('api/notifications/list/', views.list_notifications, name='list_notifications'),
    path('api/notifications/check/', views.check_notifications, name='check_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-unread/<int:notification_id>/', views.mark_notification_unread, name='mark_notification_unread'),
    path('api/notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('api/notifications/mark-all-unread/', views.mark_all_unread, name='mark_all_unread'),
    path('api/notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('api/notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('test-error/', views.test_error, name='test_error'),
]
