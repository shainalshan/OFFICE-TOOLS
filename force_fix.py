import os

path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v4.html"

print(f"Checking {path}")
if not os.path.exists(path):
    print("File not found!")
    exit(1)

with open(path, 'rb') as f:
    raw = f.read()

# Check for the specific byte sequence of the error
target_bad = b"config.frequency=='hourly'"
target_good = b"config.frequency == 'hourly'"

if target_bad in raw:
    print("Found BAD pattern in binary.")
elif target_good in raw:
    print("Found GOOD pattern in binary.")
else:
    print("Found NEITHER pattern.")
    # Print the line to see what it is
    lines = raw.split(b'\n')
    for line in lines:
        if b"frequency" in line and b"hourly" in line:
            print(f"Current Line: {line}")

# FORCE WRITE
print("Overwriting file...")
content = raw.decode('utf-8', errors='ignore')

# Fix all 3
content = content.replace("config.frequency=='hourly'", "config.frequency == 'hourly'")
content = content.replace("config.frequency=='daily'", "config.frequency == 'daily'")
content = content.replace("config.frequency=='weekly'", "config.frequency == 'weekly'")
content = content.replace("config.auto_backup %}checked{%", "config.auto_backup %}checked{% endif %}")
content = content.replace("config.auto_backup %}checked{%\r\n                        endif %}", "config.auto_backup %}checked{% endif %}")
content = content.replace("config.auto_backup %}checked{%\n                        endif %}", "config.auto_backup %}checked{% endif %}")


with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Write complete. Verifying...")
with open(path, 'rb') as f:
    new_raw = f.read()
    
if target_good in new_raw:
    print("Verification SUCCESS: Found good pattern.")
else:
    print("Verification FAILED: Good pattern not found.")
