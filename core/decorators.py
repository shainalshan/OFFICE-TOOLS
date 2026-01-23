from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from functools import wraps
from .models import Tool, UserToolAccess
from .utils import is_feature_enabled
from .exceptions import AppError, FeatureDisabledError
import logging

logger = logging.getLogger(__name__)

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

def require_feature(feature_name, fallback_view=None):
    """
    Decorator to check if a feature is enabled.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not is_feature_enabled(feature_name):
                logger.warning(f"Access attempt to disabled feature: {feature_name} by user {request.user}")
                if request.user.is_superuser:
                    messages.warning(request, f"Feature '{feature_name}' is disabled, but you are viewing it as admin.")
                else:
                    if fallback_view:
                         return redirect(fallback_view)
                    raise FeatureDisabledError(feature_name)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def safe_view(view_func):
    """
    Decorator to wrap views in a generic try-except block.
    Captures known AppErrors and displays messages.
    Logs unexpected errors and re-raises them (so generic middleware can handle 500).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except AppError as e:
            # Handle expected application errors gracefully
            logger.error(f"AppError in {view_func.__name__}: {str(e)}")
            messages.error(request, e.message)
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        except Exception as e:
            # Log unexpected errors but let them bubble up to Global Middleware
            # UNLESS we want to stay on the same page?
            # User requirement: "know why it shouldn't work". 
            # Letting it bubble to middleware gives the best 500 page.
            logger.exception(f"Unexpected error in {view_func.__name__}: {str(e)}")
            raise e
    return _wrapped_view
