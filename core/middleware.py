import threading
import logging
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from .exceptions import AppError, FeatureDisabledError

logger = logging.getLogger(__name__)

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response

class GlobalExceptionMiddleware:
    """
    Catches all unhandled exceptions and renders a user-friendly error page.
    For superusers, it displays detailed traceback information.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Log the full error
        logger.exception(f"Unhandled exception in request: {request.path}")

        # Check for AJAX/API requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
            return JsonResponse({
                'error': True,
                'message': str(exception)
            }, status=500)

        # Context for the error page
        context = {
            'error_message': str(exception),
        }

        # Detailed debug info for admins
        if request.user.is_authenticated and request.user.is_superuser:
            context['traceback'] = traceback.format_exc()
            context['exception_type'] = type(exception).__name__

        # Handle specific custom exceptions
        if isinstance(exception, FeatureDisabledError):
             return render(request, '404_custom.html', {'message': str(exception)}, status=404)

        if isinstance(exception, AppError):
             # These are "expected" failures, maybe just warn?
             # If it reached here, it wasn't caught by safe_view.
             return render(request, '500_custom.html', context, status=500)

        # Generic 500
        return render(request, '500_custom.html', context, status=500)

class PerformanceLoggingMiddleware:
    # Optional: Log slow requests
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer?
        response = self.get_response(request)
        # End timer and log?
        return response
