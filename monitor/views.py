import json
from datetime import datetime
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import RequestLog, ErrorLog

@staff_member_required
def dashboard(request):
    """
    Main dashboard view.
    """
    # Active tools count (just for info)
    from core.models import Tool
    active_tools = Tool.objects.count()
    
    # Recent Logs (last 50)
    recent_requests = RequestLog.objects.select_related('user').order_by('-created_at')[:50]
    recent_errors = ErrorLog.objects.order_by('-created_at')[:10]
    
    context = {
        'active_tools': active_tools,
        'recent_requests': recent_requests,
        'recent_errors': recent_errors,
    }
    return render(request, 'monitor/dashboard.html', context)

@staff_member_required
def api_logs(request):
    """
    API to fetch latest logs for the table (htmx polling or JS fetch).
    """
    after_id = request.GET.get('after_id', 0)
    logs = RequestLog.objects.filter(id__gt=after_id).select_related('user').order_by('-created_at')[:20]
    
    data = []
    for log in logs:
        data.append({
            'id': log.id,
            'method': log.method,
            'path': log.path,
            'status': log.status_code,
            'time': log.response_time,
            'ip': log.ip_address,
            'user': log.user.username if log.user else 'Anonymous',
            'created_at': log.created_at.strftime('%H:%M:%S')
        })
    
    return JsonResponse({'logs': data})

import csv
from django.http import HttpResponse

@staff_member_required
def export_report(request):
    """
    Export logs for a specific date as CSV.
    """
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponse('Date is required', status=400)
        
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse('Invalid date format', status=400)
        
    # Filter logs
    logs = RequestLog.objects.filter(created_at__date=date).order_by('created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="server_report_{date_str}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Time', 'IP', 'Method', 'Path', 'Status', 'Latency', 'User'])
    
    for log in logs:
        writer.writerow([
            log.created_at.strftime('%H:%M:%S'),
            log.ip_address,
            log.method,
            log.path,
            log.status_code,
            f"{log.response_time:.4f}",
            log.user.username if log.user else 'Anonymous'
        ])
        
    return response
