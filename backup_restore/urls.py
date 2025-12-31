from django.urls import path
from . import views

urlpatterns = [
    path('', views.BackupDashboardView.as_view(), name='backup_dashboard'),
    path('configure/', views.ConfigureBackupView.as_view(), name='configure_backup'),
    path('trigger/', views.TriggerBackupView.as_view(), name='trigger_backup'),
    path('download/<int:log_id>/', views.DownloadBackupView.as_view(), name='download_backup'),
    path('restore/', views.RestoreBackupView.as_view(), name='restore_backup'),
    path('browse_path/', views.BrowsePathView.as_view(), name='browse_path'),
]
