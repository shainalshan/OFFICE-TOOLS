from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_dashboard, name='asset_dashboard'),
]
