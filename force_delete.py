import os

path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard.html"

if os.path.exists(path):
    print(f"File exists. Size: {os.path.getsize(path)} bytes")
    try:
        os.remove(path)
        print("File deleted successfully.")
    except Exception as e:
        print(f"Error deleting file: {e}")
else:
    print("File does not exist.")
