import os
import uuid
import threading
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .utils import handle_file_operation

def converter_home(request):
    return render(request, 'file_converter/home.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        operation = request.POST.get('operation')
        
        if not operation:
            return HttpResponseBadRequest("Operation not specified")

        # Save the file temporarily
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)
        
        task_id = str(uuid.uuid4())
        
        # Start background thread
        thread = threading.Thread(target=handle_file_operation, args=(operation, file_path, task_id))
        thread.daemon = True
        thread.start()
        
        return JsonResponse({'task_id': task_id, 'status': 'started'})
    
    return HttpResponseBadRequest("No file uploaded")

def get_task_status(request, task_id):
    status_data = cache.get(f"task_{task_id}")
    if not status_data:
        return JsonResponse({'status': 'unknown', 'message': 'Task not found or expired'})
    
    response_data = status_data.copy()
    
    if status_data['status'] == 'completed':
        result_path = cache.get(f"result_{task_id}")
        if result_path:
            from django.urls import reverse
            response_data['download_url'] = reverse('download_file', args=[task_id])
            
    return JsonResponse(response_data)

def download_file(request, task_id):
    result_path = cache.get(f"result_{task_id}")
    if result_path and os.path.exists(result_path):
        return FileResponse(open(result_path, 'rb'), as_attachment=True)
    return HttpResponseBadRequest("File not found or expired")
