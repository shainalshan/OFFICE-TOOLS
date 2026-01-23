
import re

def find_unclosed_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Regex for tags
    tag_re = re.compile(r'{%\s*(\w+)')
    end_tag_re = re.compile(r'{%\s*end(\w+)')

    # Tags that require closing
    block_tags = {
        'if': 'endif',
        'for': 'endfor',
        'block': 'endblock',
        'with': 'endwith',
        'while': 'endwhile' # non-standard but for completeness
    }

    for i, line in enumerate(lines):
        # Find all tags in line
        # Note: simplistic parsing, doesn't handle multiple tags on one line well if nested
        # But good enough for this file structure
        
        matches = list(re.finditer(r'{%\s*(\w+)\s*.*?:?\s*%}', line))
        
        for match in matches:
            tag_name = match.group(1)
            
            if tag_name in block_tags:
                stack.append((tag_name, i + 1, line.strip()))
            
            elif tag_name.startswith('end'):
                expected_end = tag_name
                base_tag = tag_name[3:]
                
                if stack:
                    last_tag, last_line, last_content = stack[-1]
                    if block_tags.get(last_tag) == expected_end:
                        stack.pop()
                    else:
                        print(f"MISMATCH at line {i+1}: Found {tag_name}, expected {block_tags.get(last_tag)} for '{last_tag}' from line {last_line}")
                else:
                    print(f"ORPHAN END TAG at line {i+1}: {tag_name}")

    if stack:
        print("\nUNCLOSED TAGS DETECTED:")
        for tag, line_num, content in stack:
            print(f"Line {line_num}: {tag} (Content: {content})")
    else:
        print("No unclosed tags found.")

if __name__ == "__main__":
    find_unclosed_tags(r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v6.html")
