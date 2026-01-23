from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_home, name='contact_home'),
    path('add/', views.add_contact, name='add_contact'),
    path('edit/<int:contact_id>/', views.edit_contact, name='edit_contact'),
    path('delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('download/', views.download_vcf, name='download_vcf'),
    path('search/', views.search_contacts, name='search_contacts'),
]
