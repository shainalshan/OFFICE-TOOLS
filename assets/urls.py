from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_dashboard, name='asset_dashboard'),
    path('api/manage/', views.api_manage_asset, name='api_manage_asset'),
    path('export/', views.export_assets, name='export_assets'),
    path('audit/', views.audit_dashboard, name='audit_dashboard'),
    path('audit/start/', views.start_audit, name='start_audit'),
    path('audit/session/<int:session_id>/', views.audit_session, name='audit_session'),
    path('audit/api/', views.api_audit_action, name='api_audit_action'),
    path('audit/complete/<int:session_id>/', views.complete_audit, name='complete_audit'),
]
