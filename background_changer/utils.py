
import os
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    
from PIL import Image
import io

def process_image(input_image_path, background_template_path, output_path):
    """
    Removes background from input_image and composites it onto background_template.
    """
    try:
        if not REMBG_AVAILABLE:
            print("rembg library is not installed.")
            return False

        # Open Input Image
        with open(input_image_path, 'rb') as i:
            input_data = i.read()
            
        # Remove Background
        subject_data = remove(input_data)
        subject_img = Image.open(io.BytesIO(subject_data)).convert("RGBA")
        
        # Open Background Template
        bg_img = Image.open(background_template_path).convert("RGBA")
        
        # Resize Subject to fit/match background?
        # Strategy: Scale subject to fit within the background, maybe 80% height?
        # Or just paste it? User said "pre build back ground image will be the background that human back ground"
        # Assuming we want the human to look like they are in that background.
        
        bg_w, bg_h = bg_img.size
        s_w, s_h = subject_img.size
        
        # Determine scale factor to make subject fit nicely (e.g. 90% of height)
        # But don't upscale if subject is small? Maybe just center it.
        # Let's try to fit height to 85% of background height
        target_h = int(bg_h * 0.85)
        aspect_ratio = s_w / s_h
        target_w = int(target_h * aspect_ratio)
        
        subject_img_resized = subject_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Position: Center horizontally, Bottom aligned (with small padding)
        pos_x = (bg_w - target_w) // 2
        pos_y = bg_h - target_h # Bottom aligned
        
        # Create a copy of background to paste onto
        final_img = bg_img.copy()
        final_img.paste(subject_img_resized, (pos_x, pos_y), subject_img_resized)
        
        # Save Result
        final_img = final_img.convert("RGB") # Save as non-transparent for final result usually
        final_img.save(output_path, quality=95)
        
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False
