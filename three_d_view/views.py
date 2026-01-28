from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Project3D
from django.conf import settings
from core.decorators import check_tool_access

@login_required
@check_tool_access('3d-view')
def project_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        model_file = request.FILES.get('model_file')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if name and model_file:
            Project3D.objects.create(
                name=name,
                model_file=model_file,
                latitude=float(latitude) if latitude else 25.2048,
                longitude=float(longitude) if longitude else 55.2708,
                owner=request.user
            )
            return redirect('three_d_view:project_list')
            
    projects = Project3D.objects.all().order_by('-created_at')
    return render(request, 'three_d_view/project_list.html', {'projects': projects})

@login_required
def map_view(request):
    return render(request, 'three_d_view/map.html', {
        'cesium_token': getattr(settings, 'CESIUM_ION_TOKEN', '')
    })

@login_required
def api_projects(request):
    data = []
    projects = Project3D.objects.all()
    for p in projects:
        data.append({
            'id': p.id,
            'name': p.name,
            'url': p.model_file.url,
            'lat': p.latitude,
            'lon': p.longitude,
            'alt': p.altitude,
            'heading': p.heading,
            'scale': p.scale
        })
    return JsonResponse({'projects': data})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project3D, id=project_id)
    project.delete()
    return redirect('three_d_view:project_list')
