from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Asset, AuditSession, AuditLog
from contacts.models import Contact
from django.db.models import Count, Q
from django.core.paginator import Paginator
from core.decorators import check_tool_access
import openpyxl
from django.utils import timezone
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
    # Apply Category Filter
    if filter_type:
        if filter_type == 'MACBOOK':
            assets = assets.filter(device_type='MACBOOK')
        elif filter_type == 'LAPTOP':
            assets = assets.filter(device_type='LAPTOP')
        elif filter_type == 'IPHONE':
            assets = assets.filter(device_type='IPHONE')
        elif filter_type == 'ANDROID':
            assets = assets.filter(device_type='ANDROID')
        elif filter_type == 'KEYBOARD_MOUSE':
            assets = assets.filter(device_type='KEYBOARD_MOUSE')
        elif filter_type == 'OTHER':
            assets = assets.filter(device_type='OTHER')
        elif filter_type == 'IN_STORE':
            # In Store includes pure IN_STORE and RESIGNED items (as they are back in custody/history)
            assets = assets.filter(status__in=['IN_STORE', 'RESIGNED'])
        elif filter_type == 'MONITOR':
            assets = assets.filter(device_type='MONITOR')
        elif filter_type == 'IN_USE':
            # "Company Asset" button now shows ALL assets regardless of status
            pass # No filter applies
        elif filter_type == 'AVAILABLE':
            # "Available" = In Store (Laptop, Macbook, iPhone, Android)
            assets = assets.filter(status='IN_STORE', device_type__in=['LAPTOP', 'MACBOOK', 'IPHONE', 'ANDROID'])
        elif filter_type == 'DAMAGED':
            assets = assets.filter(status='DAMAGED')
        elif filter_type == 'REPLACEMENT':
            assets = assets.filter(status='REPLACEMENT')
        elif filter_type == 'RESIGNED':
            assets = assets.filter(status='RESIGNED')

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
    
    mac_count = base_qs.filter(device_type='MACBOOK').count()
    laptop_count = base_qs.filter(device_type='LAPTOP').count()
    phone_count = base_qs.filter(device_type='IPHONE').count()
    android_count = base_qs.filter(device_type='ANDROID').count()
    accessory_count = base_qs.filter(device_type='KEYBOARD_MOUSE').count()
    monitor_count = base_qs.filter(device_type='MONITOR').count()
    other_count = base_qs.filter(device_type='OTHER').count()
    
    # Status Counts
    in_store_count = base_qs.filter(status='IN_STORE').count()
    # "Company Asset" count -> Total Assets in this location
    in_use_count = base_qs.count()
    
    # "Laptops Remaining" -> Now "Total Available" (Specific types)
    laptops_remaining = base_qs.filter(status='IN_STORE', device_type__in=['LAPTOP', 'MACBOOK', 'IPHONE', 'ANDROID']).count()
    
    # "Damaged" -> Status Damaged
    damaged_count = base_qs.filter(status='DAMAGED').count()
    
    # "Replacement" -> Status Replacement
    replacements_count = base_qs.filter(status='REPLACEMENT').count()

    # "Resigned" -> Status Resigned
    resigned_count = base_qs.filter(status='RESIGNED').count()
    
    # "Resigned" count if needed? User didn't ask for tile, but nice to have.
    # But wait, original code didn't have Resigned Count tile. 
    # Just used in filters?
    # I'll keep damaged/replacement counts as they are used in tiles.

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
            'laptop_count': laptop_count,
            'phone_count': phone_count,
            'android_count': android_count,
            'accessory_count': accessory_count,
            'other_count': other_count,
            'in_store_count': in_store_count,
            'in_use_count': in_use_count,
            'laptops_remaining': laptops_remaining,
            'damaged_count': damaged_count,
            'replacements_count': replacements_count,
            'resigned_count': resigned_count,
            'monitor_count': monitor_count,
            'search_query': search_query,
            'filter_type': filter_type,
        }
        return render(request, 'assets/dashboard.html', context)

    # Pagination
    paginator = Paginator(assets, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'assets': page_obj,
        'current_tab': current_tab,
        'mac_count': mac_count,
        'laptop_count': laptop_count,
        'phone_count': phone_count,
        'android_count': android_count,
        'accessory_count': accessory_count,
        'other_count': other_count,
        'in_store_count': in_store_count,
        'in_use_count': in_use_count,
        'monitor_count': monitor_count,
        'laptops_remaining': laptops_remaining,
        'damaged_count': damaged_count,
        'replacements_count': replacements_count,
        'resigned_count': resigned_count,
        'search_query': search_query,
        'filter_type': filter_type,
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
@login_required
@check_tool_access('assets')
def export_assets(request):
    # Ignoring current_tab and search_query to export absolute ALL data as requested
    # "All data below under the filter should export as excel as single file - DUBAI... INDIA... PAKISTAN... STAFF"
    
    wb = openpyxl.Workbook()
    # Remove default sheet
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
        
    locations = ['DUBAI', 'INDIA', 'PAKISTAN']
    
    # 1. Export Locations
    for loc in locations:
        ws = wb.create_sheet(title=f"{loc} DEVICE LIST")
        
        # Headers
        headers = ['MNI', 'Staff in Possession', 'Device Type', 'Brand', 'Model/Detail', 'Serial Number', 'Status', 'Signed', 'Date Issued', 'Remarks', 'Editor Name']
        ws.append(headers)
        
        assets = Asset.objects.filter(location=loc).order_by('-created_at')
        
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
                asset.remarks,
                asset.last_edited_by or '-'
            ])
            
    # 2. Export Staff List
    ws_staff = wb.create_sheet(title="STAFF LIST")
    staff_headers = ['Staff No', 'Staff Name', 'Total Pixl Devices', 'Personal Devices', 'Total']
    ws_staff.append(staff_headers)
    
    staff_qs = Contact.objects.all().order_by('name')
    for s in staff_qs:
        pixl_count = Asset.objects.filter(assigned_to_email__iexact=s.name).count()
        ws_staff.append([
            s.staff_no or '-',
            s.name,
            pixl_count,
            s.personal_devices or '-',
            pixl_count # Total logic
        ])
    
    # Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Global_Assets_Export.xlsx"'
    wb.save(response)
    return response

from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date

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
        
        if not serial_number:
            return JsonResponse({'status': 'error', 'message': 'Serial Number is required.'}, status=400)

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
                status = 'IN_STORE'
        
        is_signed = data.get('is_signed', False)
        # Parse Dates
        date_issued_str = data.get('date_issued')
        date_issued = parse_date(date_issued_str) if date_issued_str else None
        
        remarks = data.get('remarks', '')
        # Clean staff email/name
        staff_name = staff_name.strip() if staff_name else ''
        location = data.get('location', 'DUBAI') # Default/Active Tab
        
        # Get Editor Name
        editor_name = request.user.first_name if request.user.first_name else request.user.username
        
        if action == 'add':
            # Validation
            # Validation
            # (Legacy duplicate check removed here, using new unified check below)
            
            # Resigned Validation
            if device_type == 'RESIGNED':
                if not staff_name:
                    return JsonResponse({'status': 'error', 'message': 'Staff in Possession is mandatory for Resigned assets.'}, status=400)
                status = 'IN_USE' # Resigned means it was with someone, so logically IN_USE/inactive.
            # Check for duplicate serial number if creating new
            # Check for duplicate serial number if creating new
            existing_asset = Asset.objects.filter(serial_number=serial_number).first()
            if existing_asset:
                owner_name = existing_asset.assigned_to.username if existing_asset.assigned_to else existing_asset.assigned_to_email or "Unknown"
                
                if existing_asset.status == 'RESIGNED':
                    # Auto-archive the old resigned asset to free up the Serial Number
                    existing_asset.serial_number = f"{existing_asset.serial_number}_RESIGNED_{existing_asset.id}"
                    existing_asset.remarks = f"{existing_asset.remarks} (Archived for reuse on {timezone.now().date()})"
                    existing_asset.save()
                    # Proceed with creating new asset
                
                elif existing_asset.status == 'IN_USE':
                     return JsonResponse({
                        'status': 'error', 
                        'message': f"This device ({serial_number}) belongs to {owner_name}. Please change status to Resigned first."
                    }, status=400)
                else:
                    # In Store, Damaged etc.
                    return JsonResponse({
                        'status': 'error', 
                        'message': f"Asset with this S/N already exists ({existing_asset.get_status_display()}). Please edit the existing record."
                    }, status=400)

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
            # Check unique serial if changed
            if serial_number != asset.serial_number:
                existing_with_sn = Asset.objects.filter(serial_number=serial_number).exclude(id=asset_id).first()
                if existing_with_sn:
                    owner_name = existing_with_sn.assigned_to.username if existing_with_sn.assigned_to else existing_with_sn.assigned_to_email or "Unknown"
                    
                    if existing_with_sn.status == 'RESIGNED':
                        # Auto-archive
                        existing_with_sn.serial_number = f"{existing_with_sn.serial_number}_RESIGNED_{existing_with_sn.id}"
                        existing_with_sn.remarks = f"{existing_with_sn.remarks} (Archived for reuse on {timezone.now().date()})"
                        existing_with_sn.save()
                        # Proceed with update
                        
                    elif existing_with_sn.status == 'IN_USE':
                         return JsonResponse({
                            'status': 'error', 
                            'message': f"This device ({serial_number}) belongs to {owner_name}. Please change the status first."
                        }, status=400)
                    else:
                        return JsonResponse({'status': 'error', 'message': f"Asset with this S/N already exists ({existing_with_sn.get_status_display()})."}, status=400)

            # Auto-set returned_at if status changes to terminal
            if status in ['RESIGNED', 'DAMAGED', 'REPLACEMENT']:
                 if asset.status not in ['RESIGNED', 'DAMAGED', 'REPLACEMENT']:
                    asset.returned_at = timezone.now()
            else:
                 # If moving back to IN_STORE, IN_USE, etc., clear the returned date
                 asset.returned_at = None

             # Resigned Validation
            if device_type == 'RESIGNED':
                if not staff_name:
                    return JsonResponse({'status': 'error', 'message': 'Staff in Possession is mandatory for Resigned assets.'}, status=400)
                # Resigned status override? The user might have selected 'Resigned' status in dropdown.
                # If device_type is Resigned (legacy), status should be Resigned or In Use?
                # Actually, we keep status as RESIGNED if device_type is RESIGNED.
                # But wait, original code forced IN_USE.
                # Let's respect the status passed from UI if it's RESIGNED.
                pass 
                
            # asset.mni = mni # MNI is auto-generated and immutable
            asset.assigned_to_email = staff_name 
            asset.device_type = device_type
            asset.brand = brand
            asset.model_detail = model_detail
            asset.serial_number = serial_number
            # Only update status if explicitly passed, or if legacy device type logic applies
            if provided_status:
                asset.status = status
            elif device_type == 'DAMAGED':
                asset.status = 'DAMAGED'
            
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
                'returned_at': str(asset.returned_at) if asset.returned_at else None,
                'remarks': asset.remarks,
                'last_edited_by': asset.last_edited_by,
                'location': asset.location,
                'last_edited_by': asset.last_edited_by,
                'returned_at': asset.returned_at.strftime('%Y-%m-%d %H:%M') if asset.returned_at else ''
            },
            'stats': {
                'mac_count': Asset.objects.filter(location=location, device_type='MACBOOK').count(),
                'laptop_count': Asset.objects.filter(location=location, device_type='LAPTOP').count(),
                'phone_count': Asset.objects.filter(location=location, device_type='IPHONE').count(),
                'android_count': Asset.objects.filter(location=location, device_type='ANDROID').count(),
                'accessory_count': Asset.objects.filter(location=location, device_type='KEYBOARD_MOUSE').count(),
                'monitor_count': Asset.objects.filter(location=location, device_type='MONITOR').count(),
                'other_count': Asset.objects.filter(location=location, device_type='OTHER').count(),
                'in_store_count': Asset.objects.filter(location=location, status__in=['IN_STORE', 'RESIGNED']).count(),
                'in_use_count': Asset.objects.filter(location=location).count(),
                'in_use_count': Asset.objects.filter(location=location, status='IN_USE').count(),
                'in_use_count': Asset.objects.filter(location=location, status='IN_USE').count(),
                'laptops_remaining': Asset.objects.filter(location=location, status='IN_STORE', device_type__in=['LAPTOP', 'MACBOOK', 'IPHONE', 'ANDROID']).count(),
                'damaged_count': Asset.objects.filter(location=location, status='DAMAGED').count(),
                'replacements_count': Asset.objects.filter(location=location, status='REPLACEMENT').count(),
                'resigned_count': Asset.objects.filter(location=location, status='RESIGNED').count()
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@check_tool_access('assets')
def audit_dashboard(request):
    sessions = AuditSession.objects.all().order_by('-start_date')
    return render(request, 'assets/audit_dashboard.html', {'sessions': sessions})

@login_required
@check_tool_access('assets')
def start_audit(request):
    location = request.GET.get('location', 'DUBAI')
    # Check if open session exists
    existing = AuditSession.objects.filter(location=location, status='IN_PROGRESS').first()
    if existing:
        return redirect('audit_session', session_id=existing.id)
    
    session = AuditSession.objects.create(
        location=location,
        initiated_by=request.user,
        status='IN_PROGRESS'
    )
    return redirect('audit_session', session_id=session.id)

@login_required
@check_tool_access('assets')
def audit_session(request, session_id):
    session = get_object_or_404(AuditSession, id=session_id)
    
    # Get all assets for this location
    all_assets = Asset.objects.filter(location=session.location)
    total_assets = all_assets.count()
    
    # Get logs for this session
    logs = AuditLog.objects.filter(session=session)
    audited_ids = logs.values_list('asset_id', flat=True)
    
    # Classify
    verified_ids = logs.filter(status__in=['VERIFIED', 'DAMAGED']).values_list('asset_id', flat=True)
    missing_ids = logs.filter(status='MISSING').values_list('asset_id', flat=True)
    
    # Pending Assets (Not yet in logs)
    pending_assets = all_assets.exclude(id__in=audited_ids)
    
    # Calculate progress
    audited_count = logs.count()
    progress_percent = int((audited_count / total_assets) * 100) if total_assets > 0 else 0
    
    context = {
        'session': session,
        'pending_assets': pending_assets,
        'verified_logs': logs.filter(status='VERIFIED'),
        'missing_logs': logs.filter(status='MISSING'),
        'damaged_logs': logs.filter(status='DAMAGED'),
        'progress': progress_percent,
        'total': total_assets,
        'audited_count': audited_count
    }
    return render(request, 'assets/audit_session.html', context)

@login_required
@require_POST
def api_audit_action(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        asset_id = data.get('asset_id')
        status = data.get('status', 'VERIFIED')
        
        session = get_object_or_404(AuditSession, id=session_id)
        asset = get_object_or_404(Asset, id=asset_id)
        
        # update or create log
        log, created = AuditLog.objects.update_or_create(
            session=session,
            asset=asset,
            defaults={
                'status': status,
                'scanned_at': timezone.now()
            }
        )
        
        # Update Asset last_audited if verified
        if status in ['VERIFIED', 'DAMAGED']:
            asset.last_audited = timezone.now()
            asset.save()
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@check_tool_access('assets')
def complete_audit(request, session_id):
    session = get_object_or_404(AuditSession, id=session_id)
    session.status = 'COMPLETED'
    session.completed_date = timezone.now()
    session.save()
    return redirect('audit_dashboard')
