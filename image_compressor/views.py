from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from core.decorators import check_tool_access
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io

@login_required
@check_tool_access('image-compressor')
def compress_image_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        
        # Validation: Max 5MB
        if uploaded_image.size > 5 * 1024 * 1024:
            return HttpResponse('Image is too large. Max allowed size is 5MB.', status=400)

        try:
            # Open Image
            img = Image.open(uploaded_image)
            
            # Convert to RGB (in case of RGBA/Palette) to save as JPEG
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Compression Loop
            # Target: 30-50KB (approx 30720 - 51200 bytes)
            # We aim for < 50KB.
            target_size = 50 * 1024
            quality = 95
            img_io = io.BytesIO()
            
            while quality > 5:
                img_io.seek(0)
                img_io.truncate()
                img.save(img_io, format='JPEG', quality=quality)
                
                size = img_io.tell()
                if size <= target_size:
                    break
                
                # Reduce quality
                step = 5
                if size > target_size * 2:
                    step = 10 
                quality -= step
            
            img_io.seek(0)
            
            response = HttpResponse(img_io.read(), content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename="compressed_{uploaded_image.name.split(".")[0]}.jpg"'
            return response

        except Exception as e:
            return HttpResponse(f'Compression failed: {str(e)}', status=500)

    return render(request, 'core/react_dashboard.html')
