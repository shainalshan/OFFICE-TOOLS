from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_ticket, name='create_ticket'),
    path('', views.my_tickets, name='my_tickets'),
    path('admin-panel/', views.admin_ticket_panel, name='admin_ticket_panel'),
    path('reports/', views.ticket_reports, name='ticket_reports'),
]
