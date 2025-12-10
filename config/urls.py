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
    
    path('signature/', signature_views.create_signature, name='create_signature'),
    path('signature/success/', signature_views.signature_success, name='signature_success'),
    path('signature/download/', signature_views.download_signature, name='download_signature'),
    # Ticketing
    path('tickets/', include('tickets.urls')),
    
    # Tools
    path('news/', include('news.urls')),
    path('assets/', include('assets.urls')),
    path('monitor/', include('monitor.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
