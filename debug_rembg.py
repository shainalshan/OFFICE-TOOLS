
import os
import shutil
from pathlib import Path

def test_rembg_load():
    try:
        from rembg import remove, new_session
        print("Imported rembg successfully.")
        
        # Try to initialize a session (triggers model load)
        session = new_session("u2net")
        print("Model loaded successfully.")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        
        # Attempt to clear cache if it looks like a permission/corruption issue
        u2net_path = Path.home() / '.u2net'
        if u2net_path.exists():
            print(f"Found u2net cache at: {u2net_path}")
            try:
                # We won't delete automatically in this script unless we are sure, 
                # but let's list permissions or contents?
                pass
            except Exception as delete_error:
                print(f"Could not access/delete cache: {delete_error}")

if __name__ == "__main__":
    test_rembg_load()
