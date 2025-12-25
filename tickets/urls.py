from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_ticket, name='create_ticket'),
    path('history/', views.ticket_history, name='ticket_history'),
    path('admin-panel/', views.admin_ticket_panel, name='admin_ticket_panel'),
    path('reports/', views.ticket_reports, name='ticket_reports'),
    path('delete/<str:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('manage-access/', views.manage_ticket_access, name='manage_ticket_access'),
    path('manage-assignees/', views.manage_ticket_assignees, name='manage_ticket_assignees'),
    path('<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('', views.my_tickets, name='my_tickets'),
]
