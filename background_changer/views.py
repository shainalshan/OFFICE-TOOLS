
from django.shortcuts import render
from django.http import HttpResponse
from .utils import process_composite_image
from core.decorators import check_tool_access

@check_tool_access('background-changer') # Assuming this permission/flag exists or we use generic
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('user_photo'):
        user_photo = request.FILES['user_photo']
        
        try:
            processed_image_bytes = process_composite_image(user_photo)
            
            if processed_image_bytes:
                response = HttpResponse(processed_image_bytes, content_type='image/jpeg')
                # Optional: set filename for download
                # response['Content-Disposition'] = 'inline; filename="composite_id.jpg"' 
                # User asked to "see/download it immediately", inline is good for seeing.
                return response
            else:
                return render(request, 'background_changer/upload.html', {'error': 'Error processing image. Please try again.'})
        except Exception as e:
             return render(request, 'background_changer/upload.html', {'error': f'An error occurred: {str(e)}'})

    return render(request, 'background_changer/upload.html')
