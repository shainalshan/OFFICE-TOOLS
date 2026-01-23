from django.core.management.base import BaseCommand
import os
import re

class Command(BaseCommand):
    help = 'Checks and fixes template syntax errors (specifically missing spaces around operators)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix detected errors',
        )

    def handle(self, *args, **options):
        fix = options['fix']
        base_dir = os.getcwd()
        
        # Regex to find == without spaces around it.
        # Captures (anything not space/equal)==(anything not space/equal)
        # We need to be careful about JS "===".
        # Logic: 
        # 1. Find "=="
        # 2. Check if preceded by non-space AND non-equal
        # 3. Check if followed by non-space AND non-equal
        
        # This regex matches "foo==bar", "x==1"
        # It avoids " == ", " ==", "== "
        # It avoids "===" (because correct JS usually has spaces, but if it's "x===y" that's valid JS but technically matches ==. 
        # However, we are targeting Django templates mostly.
        # A safer regex for the specific issue reported (ticket.status=='PENDING'):
        
        pattern = re.compile(r"(?<![\s=])==(?![=\s])")
        
        # Walk through all files
        for root, dirs, files in os.walk(base_dir):
            if 'venv' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    self.process_file(file_path, pattern, fix)

    def process_file(self, file_path, pattern, fix):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            new_lines = []
            modified = False
            
            for i, line in enumerate(lines):
                # Search for pattern in line
                # We specifically look for occurrences inside {% if ... %} or similar, 
                # but fixing it globally in HTML files is usually safe for "==" vs " == ".
                # JS minified code might be an issue, but source code usually has spaces.
                # Let's target the specific Django syntax error style which is usually inside {% ... %}
                
                # Check if line contains Django block
                if '{%' in line and '%}' in line:
                    matches = list(pattern.finditer(line))
                    if matches:
                        self.stdout.write(self.style.WARNING(f"Found issue in {file_path}:{i+1}"))
                        self.stdout.write(f"  Current: {line.strip()}")
                        
                        if fix:
                            # Apply fix: replace matches with " == "
                            # We use sub logic
                            new_line = pattern.sub(" == ", line)
                            new_lines.append(new_line)
                            if new_line != line:
                                modified = True
                                self.stdout.write(self.style.SUCCESS(f"  Fixed:   {new_line.strip()}"))
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            if fix and modified:
                # Reconstruct content. CAREFUL with line endings, but standard \n is safest for text mode
                new_content = '\n'.join(new_lines)
                # If original file had newline at end, preserve it (splitlines discards it)
                if content.endswith('\n'):
                    new_content += '\n'
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.stdout.write(self.style.SUCCESS(f"Saved changes to {file_path}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading {file_path}: {e}"))
