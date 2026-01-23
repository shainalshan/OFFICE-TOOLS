import os

path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v4.html"

if not os.path.exists(path):
    print("File not found.")
    exit()

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("Last 20 lines:")
for i, line in enumerate(lines[-20:]):
    print(f"{len(lines)-20+i+1}: {line.rstrip()}")

# Check for multiple endblocks
count = 0
for i, line in enumerate(lines):
    if "{% endblock %}" in line:
        count += 1
        print(f"Found endblock at line {i+1}")

print(f"Total endblocks: {count}")
