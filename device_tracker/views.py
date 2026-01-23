from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import TrackedDevice, DeviceLog

@csrf_exempt
def heartbeat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serial = data.get('serial_number')
            hostname = data.get('hostname')
            os_info = data.get('os_info')
            
            # Get or Create Device
            device, created = TrackedDevice.objects.get_or_create(
                serial_number=serial,
                defaults={'hostname': hostname, 'os_info': os_info}
            )
            
            # Update last seen and static info if changed
            device.last_seen = timezone.now()
            if hostname: device.hostname = hostname 
            device.save()
            
            # Log Data
            DeviceLog.objects.create(
                device=device,
                cpu_percent=data.get('cpu_percent', 0),
                memory_percent=data.get('memory_percent', 0),
                battery_percent=data.get('battery_percent'),
                is_charging=data.get('is_charging', False),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

def tracker_dashboard(request):
    devices = TrackedDevice.objects.all()
    # Calculate online status manually
    now = timezone.now()
    device_list = []
    for d in devices:
        is_online = (now - d.last_seen).total_seconds() < 120 # 2 mins timeout
        latest_log = d.logs.first()
        device_list.append({
            'device': d,
            'is_online': is_online,
            'log': latest_log
        })
        
    return render(request, 'device_tracker/dashboard.html', {'devices': device_list})
