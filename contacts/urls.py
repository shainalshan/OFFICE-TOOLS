from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_home, name='contact_home'),
    path('download/', views.download_vcf, name='download_vcf'),
    path('search/', views.search_contacts, name='search_contacts'),
]
