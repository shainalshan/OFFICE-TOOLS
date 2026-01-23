from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .utils import compress_html
from core.models import Tool
from core.decorators import check_tool_access
import base64
import io
import waffle
from PIL import Image

@check_tool_access('signature')
def create_signature(request):
    if request.method == 'POST':
        try:
            # Get form data
            signature_model = request.POST.get('signature_model', 'pixl')
            name = request.POST.get('name')
            designation = request.POST.get('designation')
            email = request.POST.get('email')
            phone_mobile = request.POST.get('phone_mobile')
            phone_office = request.POST.get('phone_office')
            website = request.POST.get('website')
            address = request.POST.get('address')
            calendar_link = request.POST.get('calendar_link')
            photo = request.FILES.get('photo')

            # Validate photo size (50KB = 51200 bytes)
            if photo:
                # Check for auto-crop feature flag
                if waffle.flag_is_active(request, 'signature_photo_crop'):
                    try:
                         # Open image using Pillow
                        img = Image.open(photo)
                        
                        # Convert to RGB if necessary (e.g. for PNGs with transparency)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        # Calculate center crop for square aspect ratio
                        width, height = img.size
                        new_size = min(width, height)
                        
                        # Apply a small trim to remove potential edge artifacts (e.g. black lines) from source
                        # Trimming 4 pixels total (2px from each side)
                        trim = 4 
                        if new_size > trim:
                             new_size -= trim

                        left = (width - new_size) / 2
                        top = (height - new_size) / 2
                        right = (width + new_size) / 2
                        bottom = (height + new_size) / 2

                        img = img.crop((left, top, right, bottom))
                        
                        # Resize to fixed dimension (e.g., 150x150)
                        img = img.resize((150, 150), Image.Resampling.LANCZOS)
                        
                        # Save to buffer
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=90)
                        photo_data = buffer.getvalue()
                        
                        # Base64 encode
                        photo_base64 = base64.b64encode(photo_data).decode('utf-8')
                        
                    except Exception as e:
                        print(f"Image processing error: {e}")
                        # Fallback to original behavior if processing fails
                        photo.seek(0)
                        photo_data = photo.read()
                        photo_base64 = base64.b64encode(photo_data).decode('utf-8')

                else:
                    # Original Logic (Flag OFF)
                    if photo.size > 51200:
                        # Fallback to pure React rendering with error might be tricky without passing context easily
                        # But standard non-AJAX post will reload page. 
                        # We can render the react template again? 
                        # React app won't show error unless we pass it. 
                        # For now let's hope it works or user sees backend error.
                        return HttpResponse("Error: Image too large. Please go back.", status=400)
                    
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
                'photo_base64': photo_base64,
                'calendar_link': calendar_link
            }
            
            template_name = 'signature/signature_template.html'
            if signature_model == 'invespy':
                template_name = 'signature/signature_invespy.html'
            elif signature_model == 'pixl_calendar':
                template_name = 'signature/signature_pixl_calendar.html'
                
            raw_html = render_to_string(template_name, context)
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
             # Simplistic error handling for now - pure text response or redirect with error param
            return HttpResponse(f"Error: {str(e)}", status=500)

    # GET Request: Serve React App
    return render(request, 'core/react_dashboard.html')

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
