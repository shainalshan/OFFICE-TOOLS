from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.conf import settings
from .models import Folder, Document
from .forms import FolderForm, DocumentForm
from core.decorators import check_tool_access
import os

@login_required
def doc_index(request, folder_id=None):
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, user=request.user)
        folders = Folder.objects.filter(parent=current_folder, user=request.user)
        documents = Document.objects.filter(folder=current_folder, user=request.user)
    else:
        folders = Folder.objects.filter(parent__isnull=True, user=request.user)
        documents = Document.objects.filter(folder__isnull=True, user=request.user)

    if request.method == 'POST':
        if 'create_folder' in request.POST:
            folder_form = FolderForm(request.POST)
            if folder_form.is_valid():
                folder = folder_form.save(commit=False)
                folder.user = request.user
                folder.parent = current_folder
                folder.save()
                return redirect('doc_index_folder', folder_id=folder.id) if current_folder else redirect('doc_index')
            
        elif 'upload_file' in request.POST:
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                doc = doc_form.save(commit=False)
                doc.user = request.user
                doc.folder = current_folder
                # Set title from filename if not manually provided (assuming form doesn't show title input)
                if not doc.title and doc.file:
                    doc.title = os.path.basename(doc.file.name)
                doc.save()
                return redirect('doc_index_folder', folder_id=current_folder.id) if current_folder else redirect('doc_index')
    
    folder_form = FolderForm()
    doc_form = DocumentForm()

    context = {
        'current_folder': current_folder,
        'folders': folders,
        'documents': documents,
        'folder_form': folder_form,
        'doc_form': doc_form,
        'breadcrumbs': get_breadcrumbs(current_folder),
    }
    return render(request, 'documents/index.html', context)

def get_breadcrumbs(folder):
    breadcrumbs = []
    while folder:
        breadcrumbs.insert(0, folder)
        folder = folder.parent
    return breadcrumbs

@login_required
def serve_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    if not doc.file or not os.path.exists(doc.file.path):
         return HttpResponse("File not found", status=404)
    
    # For inline preview (PDF, Images), we can try to guess content_type or let FileResponse handle it
    # Adding 'as_attachment=False' for preview
    return FileResponse(open(doc.file.path, 'rb'))

@login_required
def download_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    if not doc.file or not os.path.exists(doc.file.path):
         return HttpResponse("File not found", status=404)
    return FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=doc.title)

@login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user)
    folder_id = doc.folder.id if doc.folder else None
    doc.delete()
    if folder_id:
        return redirect('doc_index_folder', folder_id=folder_id)
    return redirect('doc_index')

@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    parent_id = folder.parent.id if folder.parent else None
    folder.delete()
    if parent_id:
        return redirect('doc_index_folder', folder_id=parent_id)
    return redirect('doc_index')
