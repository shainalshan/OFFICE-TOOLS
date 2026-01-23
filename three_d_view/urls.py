from django.urls import path
from . import views

app_name = 'three_d_view'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('map/', views.map_view, name='map_view'),
    path('api/projects/', views.api_projects, name='api_projects'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
]
