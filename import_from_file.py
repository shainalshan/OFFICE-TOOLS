import os
import django
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

def parse_vcard_block(vcard_text):
    """Parse a single VCARD block into a dictionary."""
    data = {}
    lines = vcard_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('FN:'):
            data['name'] = line[3:].strip()
        elif line.startswith('TITLE:'):
            data['designation'] = line[6:].strip()
        elif line.startswith('EMAIL:'):
            data['email'] = line[6:].strip()
        elif line.startswith('TEL;') and 'CELL' in line:
            # Extract number after the last colon
            parts = line.split(':')
            if len(parts) > 1:
                data['phone_number'] = parts[-1].strip()
        elif line.startswith('TEL;') and 'WORK' in line and 'phone_number' not in data:
             # Fallback to work phone if cell not found yet
            parts = line.split(':')
            if len(parts) > 1:
                data['phone_number'] = parts[-1].strip()
                
    return data

def import_contacts_from_file(filename='users.txt.txt'):
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(file_path):
        print(f"Error: File {filename} not found.")
        return

    print(f"Reading {filename}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
         with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    # Split by END:VCARD
    raw_cards = content.split('END:VCARD')
    print(f"Found {len(raw_cards)} potential cards.")

    count = 0
    updated = 0
    skipped = 0

    for card in raw_cards:
        if 'BEGIN:VCARD' not in card:
            continue

        data = parse_vcard_block(card)
        name = data.get('name')
        
        if not name:
            continue

        # Check existing
        criteria = {}
        if data.get('email'):
            criteria['email'] = data['email']
        elif data.get('phone_number'):
            criteria['phone_number'] = data['phone_number']
        else:
            criteria['name'] = name # Fallback
            
        contact = None
        if 'email' in criteria:
            contact = Contact.objects.filter(email=criteria['email']).first()
        if not contact and 'phone_number' in criteria:
            contact = Contact.objects.filter(phone_number=criteria['phone_number']).first()
        if not contact and 'name' in criteria:
            contact = Contact.objects.filter(name=criteria['name']).first()
            
        if contact:
            # Update Logic
            changed = False
            if 'designation' in data and data['designation'] and data['designation'] != contact.designation:
                contact.designation = data['designation']
                changed = True
            if 'phone_number' in data and data['phone_number'] and not contact.phone_number:
                contact.phone_number = data['phone_number']
                changed = True
            
            if changed:
                contact.save()
                updated += 1
                # print(f"Updated: {name}")
            else:
                skipped += 1
        else:
            # Create Logic
            Contact.objects.create(
                name=name,
                designation=data.get('designation', ''),
                email=data.get('email', ''),
                phone_number=data.get('phone_number', '')
            )
            count += 1
            print(f"Created: {name}")

    print(f"\n--- SUMMARY ---")
    print(f"Created: {count}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")

if __name__ == '__main__':
    import_contacts_from_file()
