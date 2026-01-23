from django.urls import path
from . import views

urlpatterns = [
    path('', views.converter_home, name='converter_home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('status/<str:task_id>/', views.get_task_status, name='get_task_status'),
    path('download/<str:task_id>/', views.download_file, name='download_file'),
]
