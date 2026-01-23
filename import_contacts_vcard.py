import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

def parse_vcard(file_path):
    contacts_data = []
    current_contact = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('BEGIN:VCARD'):
            current_contact = {}
        elif line.startswith('END:VCARD'):
            if current_contact.get('name'):
                contacts_data.append(current_contact)
        elif line.startswith('FN:'):
            current_contact['name'] = line[3:]
        elif line.startswith('TITLE:'):
            current_contact['designation'] = line[6:]
        elif line.startswith('EMAIL'):
            # Handle EMAIL;TYPE=...:email or EMAIL:email
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_contact['email'] = parts[1]
        elif line.startswith('TEL'):
            # Handle TEL;TYPE=...:number or TEL:number
            # We only want the first number if multiple exist, or we can logic this better later
            # For now, if we already have a number, ignore subsequent ones to match the model's single field
            # Or better, append? Mmm model has 'phone_number' CharField.
            if 'phone_number' not in current_contact:
                 parts = line.split(':', 1)
                 if len(parts) > 1:
                     current_contact['phone_number'] = parts[1]
    
    return contacts_data

def run_import():
    file_path = 'users.txt.txt'
    print(f"Reading from {file_path}...")
    
    try:
        data = parse_vcard(file_path)
        print(f"Found {len(data)} contacts in file.")
        
        print("Clearing existing contacts...")
        Contact.objects.all().delete()
        
        print("Importing new contacts...")
        contacts_to_create = []
        for item in data:
            contacts_to_create.append(Contact(
                name=item.get('name', ''),
                designation=item.get('designation', ''),
                phone_number=item.get('phone_number', ''),
                email=item.get('email', '')
            ))
        
        Contact.objects.bulk_create(contacts_to_create)
        print(f"Successfully imported {len(contacts_to_create)} contacts.")
        
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")

if __name__ == "__main__":
    run_import()
