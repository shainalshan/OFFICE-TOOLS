from django.urls import path
from . import views

urlpatterns = [
    # Staff Views
    path('portal/', views.staff_portal, name='hr_staff_portal'),
    path('api/punch/', views.punch_in_out, name='hr_punch_api'),
    path('history/', views.punch_history, name='hr_punch_history'),
    
    # Timesheet Views
    path('timesheet/current/', views.current_timesheet, name='hr_current_timesheet'),
    path('timesheet/submit/', views.submit_timesheet, name='hr_submit_timesheet'),
    path('timesheet/update-entry/', views.update_timesheet_entry, name='hr_update_entry'),
    
    # HR Admin Views
    path('admin/', views.hr_admin_dashboard, name='hr_admin_dashboard'),
    path('admin/settings/', views.hr_settings, name='hr_settings'),
    path('admin/timesheets/', views.admin_timesheet_list, name='hr_admin_timesheet_list'),
    path('admin/timesheet/<int:id>/', views.admin_timesheet_detail, name='hr_admin_timesheet_detail'),
]
