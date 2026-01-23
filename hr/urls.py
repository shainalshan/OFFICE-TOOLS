from django.urls import path
from . import views

urlpatterns = [
    # Staff Views
    path('portal/', views.staff_portal, name='hr_staff_portal'),
    path('punch/api/', views.punch_in_out, name='hr_punch_api'),
    path('history/', views.punch_history, name='hr_punch_history'),
    
    # Timesheet Views
    path('timesheet/current/', views.current_timesheet, name='hr_current_timesheet'),
    path('timesheet/submit/', views.submit_timesheet, name='hr_submit_timesheet'),
    path('entry/update/', views.update_timesheet_entry, name='hr_update_entry'),
    path('timesheet/approve/', views.handle_timesheet_approval, name='hr_handle_approval'),
    path('timesheet/view/<int:timesheet_id>/', views.admin_view_timesheet, name='hr_admin_view_timesheet'),
    path('timesheet/export/<int:timesheet_id>/', views.export_timesheet_excel, name='hr_export_timesheet_excel'),
    path('timesheet/pull/', views.pull_timesheet, name='hr_pull_timesheet'),
    
    # Face Biometric
    path('face/enroll/', views.enroll_face, name='hr_enroll_face'),
    path('face/punch/', views.face_punch, name='hr_face_punch'),
    path('face/reset/', views.reset_face, name='hr_reset_face'),
    
    # Admin
    path('admin/', views.hr_admin_dashboard, name='hr_admin_dashboard'),
    path('admin/settings/', views.hr_settings, name='hr_settings'),
    path('attendance/report/', views.attendance_report, name='hr_attendance_report'),
    # path('admin/timesheets/', views.admin_timesheet_list, name='hr_admin_timesheet_list'),
    # path('admin/timesheet/<int:id>/', views.admin_timesheet_detail, name='hr_admin_timesheet_detail'),
]
# Force reload
