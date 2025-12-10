from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='monitor_dashboard'),
    path('api/logs/', views.api_logs, name='api_logs'),
    path('export/', views.export_report, name='export_report'),
]
