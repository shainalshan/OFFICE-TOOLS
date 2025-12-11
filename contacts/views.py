from django.shortcuts import render
from django.http import HttpResponse
from .models import Contact

def contact_home(request):
    return render(request, 'contacts/index.html')

import zipfile
import io

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
            vcard_data += f"ORG:{contact.designation}\n" # Also add to ORG for better visibility
        vcard_data += f"TEL;TYPE=CELL,VOICE:{contact.phone_number}\n"
        if contact.email:
            vcard_data += f"EMAIL;TYPE=WORK,INTERNET:{contact.email}\n"
        vcard_data += "END:VCARD\n"

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('company_contacts.vcf', vcard_data)
    
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
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
