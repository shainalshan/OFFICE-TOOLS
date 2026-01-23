import re
import os

path = r"tickets\templates\tickets\ticket_detail.html"
if not os.path.exists(path):
    print(f"Error: {path} not found")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original_content = content

# Fix 1: Assigned to
# Match {{ ticket.assigned_to.username [newline spaces] }}
content = re.sub(r"\{\{\s*ticket\.assigned_to\.username\s*\n\s*\}\}", "{{ ticket.assigned_to.username }}", content)

# Fix 2: Created at
# Match {{ [newline spaces] comment.created_at|timesince }}
content = re.sub(r"\{\{\s*\n\s*comment\.created_at\|timesince\s*\}\}", "{{ comment.created_at|timesince }}", content)

if content != original_content:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched ticket_detail.html")
else:
    print("No patterns matched. File might already be fixed or regex is slightly off.")

# Debug: Print the relevant lines to verify
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "ticket.assigned_to.username" in line or "comment.created_at|timesince" in line:
            print(f"Line {i+1}: {line.strip()}")
