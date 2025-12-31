from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Asset
from django.db.models import Count, Q
from core.decorators import check_tool_access
import openpyxl
from django.http import HttpResponse

@login_required
@check_tool_access('assets')
def asset_dashboard(request):
    # Default to Dubai if no tab selected
    current_tab = request.GET.get('tab', 'DUBAI').upper()
    
    search_query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')
    
    # Filter assets by location
    assets = Asset.objects.filter(location=current_tab).order_by('-created_at')

    # Apply Category Filter
    if filter_type:
        if filter_type == 'MAC':
            assets = assets.filter(device_type='MAC')
        elif filter_type == 'WINDOWS':
            assets = assets.filter(device_type='WINDOWS')
        elif filter_type == 'IPHONE':
            assets = assets.filter(device_type='IPHONE')
        elif filter_type == 'OTHER':
            assets = assets.filter(device_type='OTHER')
        elif filter_type == 'AVAILABLE':
            # "Available" = Windows/Mac in Store (as per previous logic)
            assets = assets.filter(device_type__in=['WINDOWS', 'MAC'], status='IN_STORE')
        elif filter_type == 'DAMAGED':
            assets = assets.filter(device_type='DAMAGED')
        elif filter_type == 'REPLACEMENT':
            assets = assets.filter(device_type='REPLACEMENT')

    if search_query:
        assets = assets.filter(
            Q(mni__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query) |
            Q(assigned_to_email__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model_detail__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(remarks__icontains=search_query)
        )
    
    # Stats (Filtered by current location)
    base_qs = Asset.objects.filter(location=current_tab)
    
    mac_count = base_qs.filter(device_type='MAC').count()
    windows_count = base_qs.filter(device_type='WINDOWS').count()
    phone_count = base_qs.filter(device_type='IPHONE').count()
    other_count = base_qs.filter(device_type='OTHER').count()
    
    # "Laptops Remaining" logic needs review. Is "Laptop" still a thing? 
    # User said: "Device Type... Windows, Mac, iPhone, Other".
    # So "Available" probably means "Windows + Mac" in store? Or just all IN_STORE?
    # Original logic: device_type='LAPTOP', status='IN_STORE'.
    # I'll update to: (device_type='WINDOWS' OR device_type='MAC') AND status='IN_STORE'.
    # Assuming iPhone/Other don't count as "Laptops Remaining".
    laptops_remaining = base_qs.filter(device_type__in=['WINDOWS', 'MAC'], status='IN_STORE').count()
    
    # "Damaged" -> Device Type Damaged
    damaged_count = base_qs.filter(device_type='DAMAGED').count()
    
    # "Replacement" -> Device Type Replacement
    replacements_count = base_qs.filter(device_type='REPLACEMENT').count()

    if current_tab == 'STAFF LIST':
        # Fetch from Contact DB model which is now synced
        from contacts.models import Contact
        staff_qs = Contact.objects.all().order_by('name')
        
        # We need to manually calculate asset counts since they are in Asset model
        staff_data = []
        for s in staff_qs:
            # Count assets assigned to this person (by email/name match)
            # Logic in import_assets was: assigned_to_email=staff_name
            # So simple string match
            pixl_count = Asset.objects.filter(assigned_to_email__iexact=s.name).count()
            
            staff_data.append({
                'id': s.id,
                'staff_no': s.staff_no or '-',
                'name': s.name,
                'pixl_devices': pixl_count,
                'personal_devices': s.personal_devices or '-',
                # Total logic? Maybe just pixl? Or sum?
                # User had "Total" column in Excel. Let's just show Pixl count for now.
                'total': pixl_count 
            })

        context = {
            'assets': [], 
            'staff_list': staff_data, 
            'current_tab': current_tab,
            'mac_count': mac_count,
            'windows_count': windows_count,
            'phone_count': phone_count,
            'other_count': other_count,
            'laptops_remaining': laptops_remaining,
            'damaged_count': damaged_count,
            'replacements_count': replacements_count,
            'replacements_count': replacements_count,
            'search_query': search_query,
            'filter_type': filter_type,
        }
        return render(request, 'assets/dashboard.html', context)

    context = {
        'assets': assets,
        'current_tab': current_tab,
        'mac_count': mac_count,
        'windows_count': windows_count,
        'phone_count': phone_count,
        'other_count': other_count,
        'laptops_remaining': laptops_remaining,
        'damaged_count': damaged_count,
        'replacements_count': replacements_count,
        'search_query': search_query,
        'filter_type': filter_type,
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
@check_tool_access('assets')
def export_assets(request):
    current_tab = request.GET.get('tab', 'DUBAI').upper()
    search_query = request.GET.get('q', '')
    
    # Filter Same as Dashboard
    assets = Asset.objects.filter(location=current_tab).order_by('-created_at')
    if search_query:
        assets = assets.filter(
            Q(mni__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query) |
            Q(assigned_to_email__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model_detail__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(remarks__icontains=search_query)
        )
        
    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{current_tab} Assets"
    
    # Headers
    headers = ['MNI', 'Staff in Possession', 'Device Type', 'Brand', 'Model/Detail', 'Serial Number', 'Status', 'Signed', 'Date Issued', 'Remarks']
    ws.append(headers)
    
    for asset in assets:
        staff = asset.assigned_to.username if asset.assigned_to else (asset.assigned_to_email or '-')
        signed = 'Yes' if asset.is_signed else 'No'
        date_str = asset.date_issued.strftime('%Y-%m-%d') if asset.date_issued else '-'
        
        ws.append([
            asset.mni,
            staff,
            asset.get_device_type_display(),
            asset.brand,
            asset.model_detail,
            asset.serial_number,
            asset.get_status_display(),
            signed,
            date_str,
            asset.remarks
        ])
    
    # Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Assets_{current_tab}.xlsx"'
    wb.save(response)
    return response

from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST

@login_required
@require_POST
def api_manage_asset(request):
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        # Common fields
        mni = data.get('mni', '')
        staff_name = data.get('staff_name', '')
        # Default fallback to OTHER if not found
        device_type = data.get('device_type', 'OTHER')
        brand = data.get('brand', '')
        model_detail = data.get('model_detail', '')
        serial_number = data.get('serial_number', '')
        # Status is now derived from Device Type for the Unified Logic
        # We can still accept it if needed, but per requirements "Intelligent Logic", we derive it.
        # status = data.get('status', 'IN_STORE') 
        
        # Determine Status
        # Priority: Manual Input > Auto Derived
        provided_status = data.get('status')
        
        if provided_status:
            status = provided_status
            # Auto-correction for specific types if needed, but Manual override should prevent confusion
            if device_type == 'DAMAGED':
                status = 'DAMAGED' # Force damaged for consistency
        else:
            # Fallback Auto Logic
            if device_type == 'DAMAGED':
                status = 'DAMAGED'
            elif device_type == 'REPLACEMENT':
                status = 'REPAIR'
            else:
                status = 'IN_STORE'
        is_signed = data.get('is_signed', False)
        date_issued = data.get('date_issued') or None
        remarks = data.get('remarks', '')
        location = data.get('location', 'DUBAI') # Default/Active Tab
        
        # Get Editor Name
        editor_name = request.user.first_name if request.user.first_name else request.user.username
        
        if action == 'add':
            # Validation
            existing_with_sn = Asset.objects.filter(serial_number=serial_number).first()
            if existing_with_sn:
                # Exception Rule: Allow reuse only if existing is 'REPLACEMENT'
                if existing_with_sn.device_type != 'REPLACEMENT':
                     return JsonResponse({'status': 'error', 'message': 'This serial number already exists and is currently assigned. You cannot add this device again until it is replaced or properly released.'}, status=400)
            
            # Resigned Validation
            if device_type == 'RESIGNED':
                if not staff_name:
                    return JsonResponse({'status': 'error', 'message': 'Staff in Possession is mandatory for Resigned assets.'}, status=400)
                status = 'IN_USE' # Resigned means it was with someone, so logically IN_USE/inactive.
            
            asset = Asset.objects.create(
                # mni is set after creation
                assigned_to_email=staff_name, 
                device_type=device_type,
                brand=brand,
                model_detail=model_detail,
                serial_number=serial_number,
                status=status,
                is_signed=is_signed,
                date_issued=date_issued,
                remarks=remarks,
                location=location,
                last_edited_by=editor_name
            )
            # Auto-generate MNI
            asset.mni = str(asset.id).zfill(5)
            asset.save()
            
            message = "Asset created successfully."

        elif action == 'edit':
            asset_id = data.get('asset_id')
            asset = get_object_or_404(Asset, id=asset_id)
            
            # Check unique serial if changed
            if serial_number != asset.serial_number:
                existing_with_sn = Asset.objects.filter(serial_number=serial_number).exclude(id=asset_id).first()
                if existing_with_sn:
                     if existing_with_sn.device_type != 'REPLACEMENT':
                        return JsonResponse({'status': 'error', 'message': 'This serial number already exists and is currently assigned.'}, status=400)

            # Resigned Validation
            if device_type == 'RESIGNED':
                if not staff_name:
                    return JsonResponse({'status': 'error', 'message': 'Staff in Possession is mandatory for Resigned assets.'}, status=400)
                status = 'IN_USE'
                
            # asset.mni = mni # MNI is auto-generated and immutable
            asset.assigned_to_email = staff_name # Using email field for free text name currently
            asset.device_type = device_type
            asset.brand = brand
            asset.model_detail = model_detail
            asset.serial_number = serial_number
            asset.status = status
            asset.is_signed = is_signed
            asset.date_issued = date_issued
            asset.remarks = remarks
            # Location is typically locked to the active tab or kept same, usually not edited across tabs in inline mode
            # But let's allow it if sent
            # asset.location = location 
            
            asset.last_edited_by = editor_name
            asset.save()
            message = "Asset updated successfully."
            
        elif action == 'edit_staff':
            from contacts.models import Contact
            staff_id = data.get('staff_id')
            contact = get_object_or_404(Contact, id=staff_id)
            
            contact.staff_no = data.get('staff_no', '')
            contact.name = data.get('name', '')
            contact.personal_devices = data.get('personal_devices', '')
            contact.save()
            
            message = "Staff updated successfully."
            
            # Recalculate stats for response
            pixl_count = Asset.objects.filter(assigned_to_email__iexact=contact.name).count()
            
            return JsonResponse({
                'status': 'success',
                'message': message,
                'staff': {
                    'id': contact.id,
                    'staff_no': contact.staff_no,
                    'name': contact.name,
                    'personal_devices': contact.personal_devices,
                    'pixl_devices': pixl_count,
                    'total': pixl_count # Adjust if total means something else
                }
            })

        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

        # Return updated row data (for Asset actions)
        return JsonResponse({
            'status': 'success',
            'message': message,
            'asset': {
                'id': asset.id,
                'mni': asset.mni,
                'staff_name': asset.assigned_to_email or (asset.assigned_to.username if asset.assigned_to else '-'),
                'device_type': asset.device_type,
                'device_type_display': asset.get_device_type_display(),
                'brand': asset.brand,
                'model_detail': asset.model_detail,
                'serial_number': asset.serial_number,
                'status': asset.status,
                'status_display': asset.get_status_display(),
                'is_signed': asset.is_signed,
                'date_issued': asset.date_issued.strftime('%Y-%m-%d') if asset.date_issued else None,
                'remarks': asset.remarks,
                'date_issued': asset.date_issued.strftime('%Y-%m-%d') if asset.date_issued else None,
                'remarks': asset.remarks,
                'location': asset.location,
                'last_edited_by': asset.last_edited_by
            },
            'stats': {
                'mac_count': Asset.objects.filter(location=location, device_type='MAC').count(),
                'windows_count': Asset.objects.filter(location=location, device_type='WINDOWS').count(),
                'phone_count': Asset.objects.filter(location=location, device_type='IPHONE').count(),
                'other_count': Asset.objects.filter(location=location, device_type='OTHER').count(),
                'laptops_remaining': Asset.objects.filter(location=location, device_type__in=['WINDOWS', 'MAC'], status='IN_STORE').count(),
                'damaged_count': Asset.objects.filter(location=location, device_type='DAMAGED').count(),
                'replacements_count': Asset.objects.filter(location=location, device_type='REPLACEMENT').count()
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
