from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import NewsItem
from .forms import NewsItemForm
from core.decorators import check_tool_access
@login_required
@check_tool_access('news')
def news_list(request):
    # Handle New Message (POST)
    if request.method == 'POST':
        # Create mutable copy to modify data
        post_data = request.POST.copy()
        
        # If title is generic "Update" (from hidden input) or empty, generate from content
        content = post_data.get('content', '')
        if post_data.get('title') == 'Update':
            # Use first 30 chars or first line
            generated_title = content.split('\n')[0][:30]
            if len(content) > 30:
                 generated_title += "..."
            post_data['title'] = generated_title if generated_title else "Update"
            
        # Inject defaults for simplified chat interface
        if 'type' not in post_data:
            post_data['type'] = 'NEWS'
        if 'is_active' not in post_data:
            post_data['is_active'] = 'on' # Checkbox value
            
        form = NewsItemForm(post_data, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.created_by = request.user
            news_item.save()
            return redirect('news_list')
        else:
             print("Form Errors:", form.errors) # Debugging
    else:
        form = NewsItemForm()

    type_filter = request.GET.get('type')
    # Chat style: Newest at top
    news = NewsItem.objects.filter(is_active=True).order_by('-created_at')
    
    if type_filter:
        news = news.filter(type=type_filter)
        
    return render(request, 'news/list.html', {'news': news, 'type_filter': type_filter, 'form': form})

@login_required
@check_tool_access('news')
def manage_news(request):
    items = NewsItem.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Handle Edit or Create
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(NewsItem, id=item_id)
            form = NewsItemForm(request.POST, request.FILES, instance=item)
        else:
            form = NewsItemForm(request.POST, request.FILES)
            
        if form.is_valid():
            news_item = form.save(commit=False)
            if not item_id:
                news_item.created_by = request.user
            news_item.save()
            messages.success(request, 'News item saved successfully.')
            return redirect('manage_news')
    else:
        form = NewsItemForm()
        
    return render(request, 'news/manage.html', {'items': items, 'form': form})

@login_required
def get_latest_news(request):
    # API for polling mechanism
    # Return active items created/modified recently? 
    # Or just return top 5 valid items JSON for client to compare?
    # Simplest: return ID and title of latest active notification
    latest = NewsItem.objects.filter(is_active=True).order_by('-created_at').first()
    if latest:
        data = {
            'id': latest.id,
            'title': latest.title,
            'type': latest.type,
            'timestamp': latest.created_at.timestamp()
        }
        return JsonResponse(data)
    return JsonResponse({})

@login_required
def check_reminders(request):
    """
    Returns active reminders that are due (time is now or past).
    Limited to last 24 hours to avoid spamming very old ones.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    cutoff = now - timedelta(hours=24)
    
    reminders = NewsItem.objects.filter(
        is_active=True,
        reminder_datetime__lte=now,
        reminder_datetime__gte=cutoff
    ).values('id', 'title', 'content', 'reminder_datetime')
    
    return JsonResponse({'reminders': list(reminders)})

@login_required
def get_messages(request):
    """
    Returns messages since a specific ID for live chat sync.
    """
    since_id = request.GET.get('since_id', 0)
    try:
        since_id = int(since_id)
    except ValueError:
        since_id = 0
        
    new_items = NewsItem.objects.filter(is_active=True, id__gt=since_id).order_by('created_at')
    
    # DEBUG PRINT
    if new_items.exists():
        print(f"API: User {request.user.username} asking since_id={since_id}. Found {new_items.count()} items: {[i.id for i in new_items]}")
    
    data = []
    for item in new_items:
        data.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'type': item.type,
            'author': item.created_by.username if item.created_by else "Unknown",
            'is_me': item.created_by == request.user,
            'created_at': item.created_at.strftime('%H:%M'), # Simple time format
            'attachment_url': item.attachment.url if item.attachment else None,
            'is_image': item.is_image
        })
        
    return JsonResponse({'messages': data})
