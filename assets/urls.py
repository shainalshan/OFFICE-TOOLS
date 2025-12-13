from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_dashboard, name='asset_dashboard'),
    path('api/manage/', views.api_manage_asset, name='api_manage_asset'),
    path('export/', views.export_assets, name='export_assets'),
]
