from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import KnowledgeBaseItem, AIFeedback
from assets.models import Asset
from contacts.models import Contact
from tickets.models import Ticket
import requests
import re
import json

# AI Engine URL (FastAPI Sidecar)
AI_ENGINE_URL = "http://127.0.0.1:8001"

def get_smart_context(query):
    """
    Retrieve context from SQL database (Assets, Contacts, Tickets) based on keywords.
    """
    context_parts = []
    
    # 1. Global Stats (if asking about counts)
    if any(x in query.lower() for x in ["how many", "count", "total"]):
         try:
             asset_count = Asset.objects.count()
             ticket_pending = Ticket.objects.filter(status='PENDING').count()
             context_parts.append(f"Global Stats: {asset_count} total assets. {ticket_pending} pending tickets.")
         except: pass

    # Clean query (remove special chars)
    words = re.findall(r'\w+', query.lower())
    # Remove insignificant words
    stopwords = {'the', 'is', 'a', 'an', 'in', 'on', 'of', 'for', 'to', 'at', 'by', 'with', 'about', 'details', 'show', 'me', 'search', 'find'}
    keywords = [w for w in words if w not in stopwords and len(w) >= 2] # Allow 2 letter words

    for word in keywords:
        # A. Search Assets (Live)
        assets = Asset.objects.filter(
            Q(serial_number__icontains=word) | 
            Q(assigned_to__username__icontains=word) | 
            Q(assigned_to__first_name__icontains=word) |
            Q(device_type__icontains=word) |
            Q(brand__icontains=word)
        )[:3]
        if assets.exists():
            for a in assets:
                assignee = a.assigned_to.username if a.assigned_to else "Unassigned"
                info = f"[ASSET] {a.brand} {a.model_detail} ({a.device_type})\n   - SN: {a.serial_number}\n   - Assigned: {assignee}\n   - Status: {a.status} ({a.location})\n"
                if info not in context_parts: context_parts.append(info)

        # B. Search Contacts (Live)
        contacts = Contact.objects.filter(
            Q(name__icontains=word) | 
            Q(designation__icontains=word) |
            Q(email__icontains=word) |
            Q(phone_number__icontains=word)
        )[:3]
        if contacts.exists():
            for c in contacts:
                info = f"[CONTACT] {c.name}\n   - Role: {c.designation}\n   - Email: {c.email}\n   - Phone: {c.phone_number}\n   - Staff #: {c.staff_no}\n"
                if info not in context_parts: context_parts.append(info)

        # C. Search Tickets (Live)
        tickets = Ticket.objects.filter(
            Q(ticket_id__icontains=word) |
            Q(issue__icontains=word) |
            Q(user__username__icontains=word) |
            Q(assigned_to__username__icontains=word) |
            Q(status__icontains=word)
        )[:3]
        if tickets.exists():
            for t in tickets:
                assignee = t.assigned_to.username if t.assigned_to else "Unassigned"
                info = f"[TICKET] {t.ticket_id} ({t.status})\n   - Priority: {t.priority}\n   - Issue: {t.issue[:100]}...\n   - Assigned To: {assignee}\n   - Created By: {t.user.username}\n"
                if info not in context_parts: context_parts.append(info)

        # D. Search Knowledge Base (Memories)
        memories = KnowledgeBaseItem.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word)
        )[:3]
        if memories.exists():
             for m in memories:
                 info = f"[MEMORY] {m.title}: {m.content}"
                 if info not in context_parts: context_parts.append(info)

    return "\n".join(context_parts)

@login_required
def ask_ai(request):
    """
    Proxy request to the local AI Engine with Smart SQL Context.
    """
    query = None
    mode = "think"
    
    # DEBUG LOGGING (Optional: Keep minimal logs for audit if needed, or remove)
    # print(f"DEBUG INCOMING: Method={request.method}")
    
    if request.method == 'POST':
        try:
            # Handle potential byte string
            body_data = request.body
            if isinstance(body_data, bytes):
                body_data = body_data.decode('utf-8')
            
            if body_data:
                data = json.loads(body_data)
                # Try multiple keys just in case
                query = data.get('message') or data.get('query') or data.get('q')
                # mode = data.get('mode', 'think') 
        except Exception as e:
            print(f"DEBUG JSON ERROR: {e}")
            pass
    
    # Fallback to GET
    if not query:
        query = request.GET.get('q') or request.GET.get('message')
        
    if not query:
        print("DEBUG FAILURE: No query found.")
        return JsonResponse({'error': 'No query provided'}, status=400)
        
    # --- MEMORY INTERCEPTOR ---
    # Check if user wants to store a memory
    clean_query = query.lower().strip()
    if clean_query.startswith("remember") or clean_query.startswith("note that"):
        try:
            # Extract content: "Remember that the wifi pass is 123" -> "the wifi pass is 123"
            content = re.sub(r'^(remember\s*(that)?|note\s*(that)?)\s*', '', query, flags=re.IGNORECASE).strip()
            if content:
                # Create Memory
                KnowledgeBaseItem.objects.create(
                    title=f"Memory from {request.user.username}",
                    content=content,
                    created_by=request.user,
                    is_global=True # For now, make chat memories global
                )
                return JsonResponse({
                    'answer': f"✅ I have stored this in my memory: '{content}'",
                    'context': []
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    # --------------------------

    try:
        # Fetch smart context based on the query
        db_context = get_smart_context(query)
        
        # Send to AI Engine
        payload = {
            'query': query, 
            'dynamic_context': db_context,
            'user_id': request.user.id if request.user.is_authenticated else 0,
            'mode': mode,
            'items': [] # Explicitly providing empty list for items
        }
        
        try:
            # Increase timeout to 300s for "Think" mode
            response = requests.post(f"{AI_ENGINE_URL}/ask", json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return JsonResponse(data)
        except requests.exceptions.ConnectionError:
            # Auto-Start Engine Logic
            import subprocess
            import sys
            try:
                # Log that we are starting
                print("AI Engine offline. Attempting auto-start...")
                subprocess.Popen([sys.executable, "-m", "uvicorn", "ai_service.engine:app", "--port", "8001", "--host", "0.0.0.0"])
                return JsonResponse({'error': 'AI Engine was offline. I have started it up for you. Please wait ~15 seconds and try asking again.'})
            except Exception as e:
                return JsonResponse({'error': f'AI Engine offline and auto-start failed: {e}'}, status=503)
        except Exception as e:
             return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def ai_chat(request):
    """
    Render the Chat UI.
    """
    return render(request, 'pixl_core/chat.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def restart_ai_engine(request):
    """
    Attempt to restart the background AI service.
    """
    import subprocess
    import sys
    try:
        # Check if already running? No, just kill and start.
        subprocess.run("taskkill /F /IM uvicorn.exe", shell=True) # Weak attempt
        subprocess.Popen([sys.executable, "-m", "uvicorn", "ai_service.engine:app", "--port", "8001", "--host", "0.0.0.0"])
        return JsonResponse({'status': 'Restart command sent.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Knowledge Base CRUD
from django.views.decorators.http import require_POST

@login_required
@require_POST
def submit_ai_feedback(request):
    try:
        data = json.loads(request.body)
        AIFeedback.objects.create(
            user=request.user,
            query=data.get('query'),
            response=data.get('response'),
            rating=data.get('rating')
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def knowledge_list(request):
    items = KnowledgeBaseItem.objects.all().order_by('-updated_at')
    return render(request, 'pixl_core/knowledge_list.html', {'items': items})

import os
import shutil
from django.conf import settings

@login_required
def knowledge_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        uploaded_file = request.FILES.get('file')
        
        if title:
            is_global = request.user.is_superuser
            created_by = request.user
            
            item = KnowledgeBaseItem.objects.create(
                title=title, 
                content=content, 
                file=uploaded_file,
                created_by=created_by,
                is_global=is_global
            )
            
            if item.file:
                old_path = item.file.path
                if is_global:
                    target_folder = os.path.join(settings.MEDIA_ROOT, 'knowledge_base', 'global')
                else:
                    target_folder = os.path.join(settings.MEDIA_ROOT, 'knowledge_base', f'user_{created_by.id}')
                
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                    
                new_filename = os.path.basename(old_path)
                new_path = os.path.join(target_folder, new_filename)
                
                try:
                    shutil.move(old_path, new_path)
                    item.file.name = os.path.join('knowledge_base', 'global' if is_global else f'user_{created_by.id}', new_filename)
                    item.save()
                except Exception as e:
                    print(f"Error moving file: {e}")

            messages.success(request, "Knowledge added. Please restart AI to re-index.")
            return redirect('knowledge_list')
        
    return render(request, 'pixl_core/knowledge_form.html')

@login_required
def knowledge_edit(request, pk):
    item = get_object_or_404(KnowledgeBaseItem, pk=pk)
    if request.method == 'POST':
        item.title = request.POST.get('title')
        item.content = request.POST.get('content')
        if request.FILES.get('file'):
            item.file = request.FILES.get('file')
        item.save()
        messages.success(request, "Knowledge updated. Run 'train_ai' to apply changes.")
        return redirect('knowledge_list')
        
    return render(request, 'pixl_core/knowledge_form.html', {'item': item})

@login_required
def knowledge_delete(request, pk):
    item = get_object_or_404(KnowledgeBaseItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted.")
        return redirect('knowledge_list')
    return render(request, 'pixl_core/knowledge_confirm_delete.html', {'item': item})
