from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Tool, UserToolAccess

def check_tool_access(tool_slug):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusers have full access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                access = request.user.tool_access
                if access.tools.filter(slug=tool_slug, is_active=True).exists():
                    return view_func(request, *args, **kwargs)
            except UserToolAccess.DoesNotExist:
                pass
            
            messages.error(request, "You do not have permission to access this tool.")
            return redirect('home')
        return _wrapped_view
    return decorator
