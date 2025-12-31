import os

file_path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v4.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    new_content = content.replace("config.frequency=='hourly'", "config.frequency == 'hourly'")
    new_content = new_content.replace("config.frequency=='daily'", "config.frequency == 'daily'")
    new_content = new_content.replace("config.frequency=='weekly'", "config.frequency == 'weekly'")
    
    if content == new_content:
        print("No changes needed or pattern not found.")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated dashboard_v4.html")

except Exception as e:
    print(f"Error: {e}")
