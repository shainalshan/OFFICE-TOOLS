
import os
from django.conf import settings
from PIL import Image, ImageFilter
import io

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: rembg not installed. Background removal will fail.")

def process_composite_image(user_image_file):
    """
    Processes the user uploaded image:
    1. Removes background using 'u2net_human_seg' model.
    2. Applies mask erosion to fix white halos.
    3. Composites onto default background.
    4. Resizes user image to 65% of background height.
    5. Positions at bottom center.
    """
    if not REMBG_AVAILABLE:
        raise ImportError("rembg library is required but not installed.")

    # 1. Load User Image
    try:
        user_img = Image.open(user_image_file).convert("RGBA")
    except Exception as e:
        print(f"Error opening user image: {e}")
        return None

    # 2. Remove Background with Human Segmentation Model
    try:
        # Create a session with the specific model for human segmentation
        session = new_session("u2net_human_seg")
        user_img_no_bg = remove(user_img, session=session)
    except Exception as e:
        print(f"Error removing background: {e}")
        return None

    # 3. Halo Fix: Mask Erosion
    try:
        # Extract Alpha Channel
        # split() returns (R, G, B, A)
        r, g, b, a = user_img_no_bg.split()
        
        # Apply MinFilter (Erosion) to the Alpha channel
        # This shrinks the white area of the mask by ~3 pixels
        eroded_a = a.filter(ImageFilter.MinFilter(3))
        
        # Merge back
        user_img_clean = Image.merge("RGBA", (r, g, b, eroded_a))
    except Exception as e:
        print(f"Error processing mask: {e}")
        # Fallback to non-eroded if filter fails
        user_img_clean = user_img_no_bg

    # 4. Load Default Background
    bg_path = os.path.join(settings.BASE_DIR, 'background remover', 'background 1.jpg.png')
    
    if not os.path.exists(bg_path):
        print(f"Background file not found at: {bg_path}")
        return None

    try:
        bg_img = Image.open(bg_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening background image: {e}")
        return None

    bg_w, bg_h = bg_img.size

    # 5. Resize User Image (65% height)
    target_h = int(bg_h * 0.65) # 65% as requested
    
    user_w, user_h = user_img_clean.size
    aspect_ratio = user_w / user_h
    target_w = int(target_h * aspect_ratio)
    
    # Resize using LANCZOS for quality
    user_img_resized = user_img_clean.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 6. Position: Horizontally centered, Absolute Bottom
    pos_x = (bg_w - target_w) // 2
    pos_y = bg_h - target_h 
    
    # 7. Paste
    final_img = bg_img.copy()
    final_img.paste(user_img_resized, (pos_x, pos_y), user_img_resized)

    # 8. Return Result as Bytes (JPEG)
    output_io = io.BytesIO()
    final_img = final_img.convert("RGB")
    final_img.save(output_io, format='JPEG', quality=95)
    output_io.seek(0)
    
    return output_io.getvalue()
