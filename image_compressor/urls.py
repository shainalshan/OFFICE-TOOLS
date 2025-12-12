from django.urls import path
from . import views

urlpatterns = [
    path('', views.compress_image_view, name='compress_image'),
]
