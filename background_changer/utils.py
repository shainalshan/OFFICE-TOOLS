import os
from django.conf import settings
from PIL import Image, ImageFilter, ImageDraw, ImageChops, ImageFont
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
    3. Composites onto default background with 3D Pop-out effect.
    """
    if not REMBG_AVAILABLE:
        raise ImportError("rembg library is required but not installed.")

    # 1. Load User Image
    try:
        user_img = Image.open(user_image_file).convert("RGBA")
    except Exception as e:
        print(f"Error opening user image: {e}")
        return None

    # 2. Remove Background with High-Precision Model
    try:
        # Switch to ISNet-General-Use (Often considered SOTA for general object/person segmentation)
        # This addresses "use very advanced python library" request.
        session = new_session("isnet-general-use")
        user_img_no_bg = remove(user_img, session=session)
    except Exception as e:
        print(f"Error removing background: {e}")
        return None

    # 3. Halo Fix: Gentle Edge Tuning
    try:
        # Extract Alpha Channel
        r, g, b, a = user_img_no_bg.split()
        
        # 1. Gentle Erosion: 1px is usually enough for ISNet to remove the anti-aliased fringe
        eroded_a = a.filter(ImageFilter.MinFilter(1))
        
        # 2. Feathering: Soft blur for natural integration
        feathered_a = eroded_a.filter(ImageFilter.GaussianBlur(1))
        
        # Merge back
        user_img_clean = Image.merge("RGBA", (r, g, b, feathered_a))
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

    # 4a. Patch Watermark (User reported "gemini icon in bottom corner")
    # We simply copy a slice of the background from slightly above the bottom edge 
    # and paste it over the bottom corners to cover any logos.
    patch_h = int(bg_h * 0.1) # 10% height patch
    patch_w = int(bg_w * 0.2) # 20% width patch
    
    # Bottom Right Patch
    # Source: Region just above the corner
    box_src_r = (bg_w - patch_w, bg_h - 2*patch_h, bg_w, bg_h - patch_h)
    patch_r = bg_img.crop(box_src_r)
    # Target: The corner itself
    box_dst_r = (bg_w - patch_w, bg_h - patch_h)
    bg_img.paste(patch_r, box_dst_r)

    # Bottom Left Patch (Just in case)
    box_src_l = (0, bg_h - 2*patch_h, patch_w, bg_h - patch_h)
    patch_l = bg_img.crop(box_src_l)
    box_dst_l = (0, bg_h - patch_h)
    bg_img.paste(patch_l, box_dst_l)

    # --- 3D POP-OUT COMPOSITION LOGIC ---
    
    # A. Define Fixed Frame Geometry (Based on Background)
    # This ensures the "hole" is always in the same place 
    frame_width = int(bg_w * 0.55) # Reduced to 55% (User requested "reduce a little bit")
    frame_radius = frame_width // 2
    bottom_margin = int(bg_h * 0.08) # 8% margin from bottom
    
    # The "Equator" is the flat top of the semi-circle graphic
    # Graphic Bottom is at: bg_h - bottom_margin
    # Graphic Top (Equator) is at: bg_h - bottom_margin - frame_radius
    graphic_cx = bg_w // 2
    graphic_cy = bg_h - bottom_margin - frame_radius # This is the center of the arc
    
    # B. Draw Graphic (Purple Semi-Circle) on Background
    # RESTORED per user instruction ("photo should be on the top of the semi circle")
    # We draw the solid purple shape first.
    final_img = bg_img.copy()
    draw_bg = ImageDraw.Draw(final_img)
    shape_color = "#804cab" 
    
    # Use EXACT radius to match the mask ("same dimension")
    r_graphic = frame_radius 
    
    # Bounding box for the graphic circle: (cx-r, cy-r, cx+r, cy+r)
    # We draw the bottom half (0 to 180 degrees)
    draw_bg.pieslice(
        (graphic_cx - r_graphic, graphic_cy - r_graphic, 
         graphic_cx + r_graphic, graphic_cy + r_graphic),
        start=0, end=180, fill=shape_color
    )
    
    # C. Draw Branding "invespy" - REMOVED per user request
    # ... (code removed) ...

    # D. Resize User Image
    # User requested "reduce width of semi circle , not the image"
    # So we keep image width at the previous scale (70% of BG) regardless of the new smaller frame (60%).
    target_w = int(bg_w * 0.70) 
    
    user_w, user_h = user_img_clean.size
    aspect_ratio = user_h / user_w
    target_h = int(target_w * aspect_ratio)
    
    user_img_resized = user_img_clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # D2. Shift User Image Downward (Per user request "more down ward until image cover semi circle", then "move upward", then "little more")
    # This moves the person further down to ensure the torso "plugs" the bottom hole completely.
    shift_y = 0 # Reduced to 0 (User requested "move little more")
    shifted_canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    shifted_canvas.paste(user_img_resized, (0, shift_y))
    user_img_resized = shifted_canvas
    
    # E. Create "Pop-Out" Mask for User Image
    # Mask size matches the ZOOMED user image: (target_w, target_h)
    # BUT the shape inside must match the FIXED FRAME dimensions.
    
    mask = Image.new("L", (target_w, target_h), 0)
    draw_mask = ImageDraw.Draw(mask)
    
    # Center of the mask circle in the ZOOMED image coordinates:
    # X: Center of image -> target_w // 2
    # Y: We want the bottom of the mask circle to align with the bottom of the image.
    #    So Center Y = target_h - frame_radius
    
    mask_radius = frame_radius # FIXED radius (not zoomed)
    local_cx = target_w // 2
    local_cy = target_h - mask_radius
    
    # Draw bottom semi-circle (White/Opaque)
    draw_mask.ellipse(
        (local_cx - mask_radius, local_cy - mask_radius, 
         local_cx + mask_radius, local_cy + mask_radius), 
        fill=255
    )
    
    # Draw top rectangle (White/Opaque)
    # Width is 2 * mask_radius (matches frame width)
    # Extends from top (0) to equator (local_cy)
    rect_left = local_cx - mask_radius
    rect_right = local_cx + mask_radius
    draw_mask.rectangle((rect_left, 0, rect_right, local_cy), fill=255)
    
    # Apply Mask
    existing_r, existing_g, existing_b, existing_a = user_img_resized.split()
    final_alpha = ImageChops.multiply(existing_a, mask)
    user_img_resized.putalpha(final_alpha)
    
    # F. Paste User Image
    # Align bottom of user image with bottom of graphic
    # Graphic bottom y = bg_h - bottom_margin
    
    pos_x = (bg_w - target_w) // 2
    pos_y = (bg_h - bottom_margin) - target_h
    
    final_img.paste(user_img_resized, (pos_x, pos_y), user_img_resized)

    # 8. Return Result as Bytes (JPEG)
    output_io = io.BytesIO()
    final_img = final_img.convert("RGB")
    final_img.save(output_io, format='JPEG', quality=95)
    output_io.seek(0)
    
    return output_io.getvalue()
