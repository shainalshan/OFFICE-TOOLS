from django.urls import path
from . import views

urlpatterns = [
    path('heartbeat/', views.heartbeat, name='tracker_heartbeat'),
    path('dashboard/', views.tracker_dashboard, name='tracker_dashboard'),
]
