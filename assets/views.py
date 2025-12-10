from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Asset
from django.db.models import Count, Q
from core.decorators import check_tool_access

@login_required
@login_required
@check_tool_access('assets')
def asset_dashboard(request):
    # Default to Dubai if no tab selected
    current_tab = request.GET.get('tab', 'DUBAI').upper()
    
    # Filter assets by location
    assets = Asset.objects.filter(location=current_tab).order_by('-created_at')
    
    # Stats (Filtered by current location)
    base_qs = Asset.objects.filter(location=current_tab)
    
    mac_count = base_qs.filter(os_type='MAC').count()
    windows_count = base_qs.filter(os_type='WINDOWS').count()
    phone_count = base_qs.filter(device_type='MOBILE').count()
    
    # "Laptops Remaining" -> In Store Laptops
    laptops_remaining = base_qs.filter(device_type='LAPTOP', status='IN_STORE').count()
    
    # "Damaged" -> Status Damaged
    damaged_count = base_qs.filter(status='DAMAGED').count()
    
    # "Replacement" -> Status Replacement or Repair
    replacements_count = base_qs.filter(status='REPAIR').count()

    context = {
        'assets': assets,
        'current_tab': current_tab,
        'mac_count': mac_count,
        'windows_count': windows_count,
        'phone_count': phone_count,
        'laptops_remaining': laptops_remaining,
        'damaged_count': damaged_count,
        'replacements_count': replacements_count,
    }
    return render(request, 'assets/dashboard.html', context)
