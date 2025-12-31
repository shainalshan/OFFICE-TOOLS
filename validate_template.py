import re

file_path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v4.html"

def validate_tags(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Simple regex to capture block tags. 
    # Valid block openers: if, for, block, with, while, etc.
    # Closers: endif, endfor, endblock, endwith, etc.
    
    # We only care about standard django blocks roughly
    tag_pattern = re.compile(r'{%\s*(if|for|block|with|while|comment|autoescape)\b')
    end_tag_pattern = re.compile(r'{%\s*(endif|endfor|endblock|endwith|endwhile|endcomment|endautoescape)\b')
    
    # Handle single line if usage? Django doesn't really have single line if without endif, except if it spans lines.
    # But usually {% if x %}y{% endif %} is fine.
    # We need to scan tokens in order.
    
    full_text = "".join(lines)
    
    # Find all tags in order
    tokens = re.finditer(r'{%\s*(\w+)', full_text)
    
    openers = {'if', 'for', 'block', 'with', 'while', 'comment', 'autoescape'}
    closers = {
        'endif': 'if',
        'endfor': 'for',
        'endblock': 'block',
        'endwith': 'with',
        'endwhile': 'while',
        'endcomment': 'comment',
        'endautoescape': 'autoescape'
    }
    
    # Map token index to line number for better error reporting
    # This is a bit lazy, let's just count newlines up to the match start
    
    for match in tokens:
        tag = match.group(1)
        pos = match.start()
        line_no = full_text.count('\n', 0, pos) + 1
        
        # print(f"DEBUG: Found {tag} at line {line_no}") # Uncomment for extreme verbosity

        if tag in openers:
            stack.append((tag, line_no))
            print(f"[{line_no}] Open: {tag} (Stack depth: {len(stack)})")
        elif tag in closers:
            expected_opener = closers[tag]
            if not stack:
                print(f"Error at line {line_no}: Found {{% {tag} %}} but no block was open.")
                continue
            
            last_opener, last_line = stack[-1]
            if last_opener == expected_opener:
                stack.pop()
                print(f"[{line_no}] Close: {tag} matching {last_opener} from {last_line}")
            else:
                # Mismatch?
                print(f"ERROR: [{line_no}] Close: {tag} but expected close for {last_opener} from {last_line}")
                
        elif tag in ['elif', 'else']:
            if not stack or stack[-1][0] != 'if':
                print(f"Error at line {line_no}: Found {{% {tag} %}} but not inside an 'if' block.")
            else:
               print(f"[{line_no}] {tag}")
               
    if stack:
        print("\nUnclosed blocks found:")
        for tag, line in stack:
            print(f"  {{% {tag} %}} opened at line {line}")
    else:
        print("\nStructure seems valid.")

if __name__ == "__main__":
    validate_tags(file_path)
