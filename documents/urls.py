from django.urls import path
from . import views

urlpatterns = [
    path('', views.doc_index, name='doc_index'),
    path('folder/<int:folder_id>/', views.doc_index, name='doc_index_folder'),
    path('document/<int:doc_id>/view/', views.serve_document, name='view_document'),
    path('document/<int:doc_id>/download/', views.download_document, name='download_document'),
    path('document/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
]
