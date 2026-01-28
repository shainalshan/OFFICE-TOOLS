import os
import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import AI_KnowledgeBase, Chat_Log
import json

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_user_level(user):
    if user.is_superuser or user.groups.filter(name='IT_Admin').exists():
        return 'H1'
    if user.is_authenticated:
        # Assuming external users might be distinguished somehow, else H2
        return 'H2'
    return 'H3' # Should not happen if login_required, but for logic consistency

@csrf_exempt
@login_required
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_question = data.get('question', '')
            
            user_level = get_user_level(request.user)
            
            # 1. Check for "Remember/Learn" command (Admin Only)
            if user_level == 'H1' and (user_question.lower().startswith('remember:') or user_question.lower().startswith('learn:')):
                try:
                    # Format: "Remember: Topic - Content"
                    parts = user_question.split(':', 1)[1].strip()
                    if '-' in parts:
                        topic, content = parts.split('-', 1)
                        AI_KnowledgeBase.objects.create(
                            topic=topic.strip(),
                            content=content.strip(),
                            access_level='H2' # Default to H2? Or H1? User didn't specify. Let's assume H2 or prompt user. 
                            # User said: "H1 admin says that - remeber it or learn it - its should store and respond based on it"
                            # I'll default to H2 for now so others can use it, or maybe H1? 
                            # Let's default to H2 as it's general knowledge usually.
                        )
                        return JsonResponse({'answer': f"I have learned about '{topic.strip()}'."})
                    else:
                        return JsonResponse({'answer': "For learning, please use format: 'Remember: Topic - Content'"})
                except Exception as e:
                    return JsonResponse({'answer': f"Error learning: {str(e)}"})

            # 2. RB-RAG Logic
            # Filter Knowledge Base
            allowed_levels = ['H3']
            if user_level in ['H1', 'H2']:
                allowed_levels.append('H2')
            if user_level == 'H1':
                allowed_levels.append('H1')
                
            knowledge = AI_KnowledgeBase.objects.filter(
                access_level__in=allowed_levels, 
                is_active=True
            )
            
            context_data = "\n".join([f"{k.topic}: {k.content}" for k in knowledge])
            
            system_instruction = f"""
            You are Pixl AI, an internal assistant for the company PIXL.
            
            YOUR KNOWLEDGE BASE:
            {context_data}
            
            RULES:
            1. You answer questions ONLY based on the Knowledge Base above.
            2. If the user asks a question that is NOT found in the Knowledge Base (even if you know the answer from your general training), you must refuse.
            3. If the user asks about general topics (politics, jokes, generic code), you must refuse.
            4. REFUSAL MESSAGE: In all refusal cases, reply with strictly: 'Restriction from admin'.
            5. Be professional, concise, and helpful within your boundaries.
            """
            
            # Call Gemini
            model = genai.GenerativeModel('gemini-1.5-flash') # Or pro
            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [system_instruction, f"User Question: {user_question}"]}
                ]
            )
            
            answer = response.text.strip()
            
            # Log Chat
            Chat_Log.objects.create(
                user=request.user,
                question=user_question,
                answer=answer
            )
            
            return JsonResponse({'answer': answer})

        except Exception as e:
            error_message = str(e)
            if 'relation' in error_message and 'does not exist' in error_message:
                return JsonResponse({'answer': "Hello! I am currently unable to access my knowledge base because the system database is not fully initialized. Please ask an administrator to run the database migrations and verify the credentials."})
            
            return JsonResponse({'answer': f"I encountered a technical issue: {error_message}"})
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def manage_knowledge_view(request):
    try:
        items = AI_KnowledgeBase.objects.all().order_by('-pk')
        return render(request, 'pixl_ai/manage_knowledge.html', {'items': items})
    except Exception as e:
        # If table doesn't exist, return empty list or error context
        error_message = str(e)
        if 'relation' in error_message and 'does not exist' in error_message:
            # Render the same template but with an error flag
            return render(request, 'pixl_ai/manage_knowledge.html', {
                'items': [], 
                'db_error': True,
                'error_msg': "Database table missing. Please run 'python manage.py migrate'."
            })
        return render(request, 'pixl_ai/manage_knowledge.html', {'items': [], 'error_msg': error_message})

