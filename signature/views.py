from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .utils import compress_html
from core.models import Tool
from core.decorators import check_tool_access
import base64

@check_tool_access('signature')
def create_signature(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            designation = request.POST.get('designation')
            email = request.POST.get('email')
            phone_mobile = request.POST.get('phone_mobile')
            phone_office = request.POST.get('phone_office')
            website = request.POST.get('website')
            address = request.POST.get('address')
            photo = request.FILES.get('photo')

            # Validate photo size (50KB = 51200 bytes)
            if photo:
                if photo.size > 51200:
                    return render(request, 'signature/form.html', {
                        'error': 'Image file is too large. Please upload an image smaller than 50KB.'
                    })
                
                # Read and encode image
                photo_data = photo.read()
                photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            else:
                photo_base64 = None

            # Render HTML signature
            context = {
                'name': name.upper(), 
                'designation': designation.upper(),
                'email': email,
                'phone_mobile': phone_mobile,
                'phone_office': phone_office,
                'website': website,
                'address': address,
                'photo_base64': photo_base64
            }
            
            raw_html = render_to_string('signature/signature_template.html', context)
            compressed_html = compress_html(raw_html)

            # Store in session
            request.session['generated_signature'] = compressed_html
            request.session['signature_name'] = name
            
            # --- NOTIFICATION SYSTEM START ---
            try:
                from core.models import NotificationEventSetting, SystemNotification
                setting = NotificationEventSetting.objects.get(event_type='SIG_CREATED')
                recipients = setting.subscribers.all()
                for user in recipients:
                    SystemNotification.objects.create(
                        recipient=user,
                        title="New Signature Created",
                        message=f"A new email signature was generated for {name} ({designation}).",
                        link="#" 
                    )
            except Exception as e:
                print(f"Notification Error: {e}") # Non-blocking
            # --- NOTIFICATION SYSTEM END ---

            return redirect('signature_success')

        except Exception as e:
            return render(request, 'signature/form.html', {
                'error': f'An error occurred: {str(e)}'
            })

    return render(request, 'signature/form.html')

@login_required
def signature_success(request):
    if 'generated_signature' not in request.session:
        return redirect('create_signature')
    return render(request, 'signature/success.html')

@login_required
def download_signature(request):
    compressed_html = request.session.get('generated_signature')
    name = request.session.get('signature_name', 'signature')
    
    if not compressed_html:
        return redirect('create_signature')

    response = HttpResponse(compressed_html, content_type='text/html')
    filename = f"signature_{name.lower().replace(' ', '_')}.html"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
