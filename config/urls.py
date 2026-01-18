from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from signature import views as signature_views
from tickets import views as ticket_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('login/', core_views.user_login, name='login'),
    path('logout/', core_views.user_logout, name='logout'),
    path('register/', core_views.register, name='register'),
    path('dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/check-users/', core_views.check_pending_users, name='check_pending_users'),
    path('tools/chat/', core_views.group_chat, name='group_chat'),
    path('tools/pdf-to-word/', core_views.pdf_to_word, name='pdf_to_word'),
    
    path('signature/', signature_views.create_signature, name='create_signature'),
    path('signature/success/', signature_views.signature_success, name='signature_success'),
    path('signature/download/', signature_views.download_signature, name='download_signature'),
    # Ticketing
    path('tickets/', include('tickets.urls')),
    path('hr/', include('hr.urls')),
    
    # Tools
    path('news/', include('news.urls')),
    path('assets/', include('assets.urls')),
    path('monitor/', include('monitor.urls')),
    path('contacts/', include('contacts.urls')),
    path('tools/compressor/', include('image_compressor.urls')),
    path('3d/', include('three_d_view.urls')),
    path('tracker/', include('device_tracker.urls')),
    path('tools/background-remover/', include('background_changer.urls')),
    path('tools/converter/', include('file_converter.urls')),
    path('backup/', include('backup_restore.urls')),
    path('backup/', include('backup_restore.urls')),
    path('pixl_ai/', include('pixl_core.urls')),


    # APIs
    path('api/notifications/search-users/', core_views.search_users_notification, name='search_users_notification'),
    path('api/notifications/list/', core_views.list_notifications, name='list_notifications'),
    path('api/notifications/check/', core_views.check_notifications, name='check_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', core_views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-unread/<int:notification_id>/', core_views.mark_notification_unread, name='mark_notification_unread'),
    path('api/notifications/mark-all-read/', core_views.mark_all_read, name='mark_all_read'),
    path('api/notifications/mark-all-unread/', core_views.mark_all_unread, name='mark_all_unread'),
    path('api/notifications/delete/<int:notification_id>/', core_views.delete_notification, name='delete_notification'),
    path('api/notifications/clear-all/', core_views.clear_all_notifications, name='clear_all_notifications'),
    path('api/tools/set/', core_views.set_user_tools, name='set_user_tools'),
    path('restore/<int:log_id>/', core_views.restore_item, name='restore_item'),
    path('profile/', core_views.profile_view, name='profile_view'),
    path('forgot-password/', core_views.forgot_password, name='forgot_password'),
    path('dashboard/theme-changer/', core_views.theme_changer_view, name='theme_changer'),
    path('dashboard/theme-changer/apply/', core_views.apply_theme, name='apply_theme'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
