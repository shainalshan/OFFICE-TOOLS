import time
import traceback
from .models import RequestLog, ErrorLog

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Capture IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        response = self.get_response(request)

        duration = time.time() - start_time
        
        # Don't log static files or admin polling to avoid spam
        # Keep it simple for now, maybe filter /static/
        if not request.path.startswith('/static/'):
            try:
                RequestLog.objects.create(
                    path=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    ip_address=ip,
                    response_time=duration,
                    user=request.user if request.user.is_authenticated else None
                )
            except Exception:
                pass # Fail silently on logging errors

        return response

    def process_exception(self, request, exception):
        try:
            ErrorLog.objects.create(
                message=str(exception),
                traceback=traceback.format_exc(),
                path=request.path
            )
        except:
            pass
        return None
