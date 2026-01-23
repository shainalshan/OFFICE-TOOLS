from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import check_tool_access
from .models import Contact
import waffle
import zipfile
import io
import re

def normalize_phone(number):
    """
    Normalizes a phone number for comparison.
    - Removes all non-digit characters.
    - Treats leading '0' as equivalent to '971'.
    - If number starts with '0', it is replaced with '971'.
    - Returns the numeric string.
    """
    if not number:
        return ""
    
    # Remove non-digits
    cleaned = re.sub(r'\D', '', str(number))
    
    # Handle Country Code Normalization (UAE specific based on user context)
    if cleaned.startswith('0'):
        cleaned = '971' + cleaned[1:]
    
    return cleaned

@login_required
def contact_home(request):
    # Allow access if user has EITHER 'contact-numbers' OR 'manage-contacts'
    can_manage = False
    if request.user.is_superuser:
        can_manage = True
    else:
        try:
            user_tools = request.user.tool_access.tools.filter(is_active=True)
            has_access = user_tools.filter(slug__in=['contact-numbers', 'manage-contacts', 'contacts']).exists()
            if not has_access:
                messages.error(request, "You do not have permission to access contact tools.")
                return redirect('home')
            
            # Check specifically for management permission
            can_manage = user_tools.filter(slug__in=['manage-contacts', 'contacts']).exists()
        except: # UserToolAccess might not exist
             messages.error(request, "You do not have permission to access contact tools.")
             return redirect('home')

    contacts = Contact.objects.all().order_by('name')
    return render(request, 'contacts/index.html', {'contacts': contacts, 'can_manage': can_manage})

# --- CRUD Operations ---
@login_required
@check_tool_access('contacts')
def add_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        designation = request.POST.get('designation')
        
        if waffle.flag_is_active(request, 'strict_contact_validation'):
            # Normalize the input number
            normalized_input = normalize_phone(phone_number)
            
            # Check against all contacts (inefficient for large DB but safe for strict mode requirement)
            # Fetch all to normalize and compare in python because DB storage is raw string
            all_contacts = Contact.objects.all()
            existing = None
            for c in all_contacts:
                if normalize_phone(c.phone_number) == normalized_input:
                    existing = c
                    break
            
            if existing:
                messages.error(request, f"This number is used by {existing.name}. Delete or edit that number then only u can add this number")
                return redirect('contact_home')

        Contact.objects.create(
            name=name,
            phone_number=phone_number,
            email=email,
            designation=designation
        )
        messages.success(request, f'Contact {name} added.')
    return redirect('contact_home')

@login_required
@check_tool_access('contacts')
def edit_contact(request, contact_id):
    if request.method == 'POST':
        contact = get_object_or_404(Contact, id=contact_id)
        contact.name = request.POST.get('name')
        new_phone_number = request.POST.get('phone_number')
        
        if waffle.flag_is_active(request, 'strict_contact_validation'):
            normalized_input = normalize_phone(new_phone_number)
            
            all_contacts = Contact.objects.exclude(id=contact_id)
            existing = None
            for c in all_contacts:
                if normalize_phone(c.phone_number) == normalized_input:
                    existing = c
                    break
            
            if existing:
                messages.error(request, f"This number is used by {existing.name}. Delete or edit that number then only u can add this number")
                return redirect('contact_home')

        contact.phone_number = new_phone_number
        contact.email = request.POST.get('email')
        contact.designation = request.POST.get('designation')
        contact.save()
        messages.success(request, f'Contact {contact.name} updated.')
    return redirect('contact_home')

@login_required
@check_tool_access('contacts')
def delete_contact(request, contact_id):
    if request.method == 'POST':
        contact = get_object_or_404(Contact, id=contact_id)
        name = contact.name
        contact.delete()
        messages.warning(request, f'Contact {name} deleted.')
    return redirect('contact_home')

def download_vcf(request):
    contacts = Contact.objects.all().order_by('name')
    vcard_data = ""
    for contact in contacts:
        # Simple name splitting for N field (Last;First;;;)
        parts = contact.name.strip().split(' ', 1)
        if len(parts) == 2:
            n_field = f"{parts[1]};{parts[0]};;;"
        else:
            n_field = f"{parts[0]};;;;"

        vcard_data += "BEGIN:VCARD\n"
        vcard_data += "VERSION:3.0\n"
        vcard_data += f"FN:{contact.name}\n"
        vcard_data += f"N:{n_field}\n"
        if contact.designation:
            vcard_data += f"TITLE:{contact.designation}\n"
            vcard_data += f"ORG:{contact.designation}\n"
        vcard_data += f"TEL;TYPE=CELL,VOICE:{contact.phone_number}\n"
        if contact.email:
            vcard_data += f"EMAIL;TYPE=WORK,INTERNET:{contact.email}\n"
        vcard_data += "END:VCARD\n"

    # Return as ZIP file containing the VCF (fixes iOS download issue)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('company_contacts.vcf', vcard_data)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="company_contacts.zip"'
    return response

from django.db.models import Q

def search_contacts(request):
    query = request.GET.get('q', '')
    if query:
        contacts = Contact.objects.filter(
            Q(name__icontains=query) | 
            Q(designation__icontains=query) | 
            Q(phone_number__icontains=query)
        ).order_by('name')
    else:
        # Default to first 20
        contacts = Contact.objects.all().order_by('name')[:20]

    return render(request, 'contacts/search.html', {'contacts': contacts, 'query': query})
