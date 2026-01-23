from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from .models import BackupConfiguration, BackupLog
from .services import BackupService
import os
import subprocess
import threading
import waffle

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class WaffleFlagMixin:
    def dispatch(self, request, *args, **kwargs):
        if not waffle.flag_is_active(request, 'new_backup_tool'):
            raise Http404("Backup tool not enabled")
        return super().dispatch(request, *args, **kwargs)

class BackupDashboardView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def get(self, request):
        config = BackupConfiguration.get_solitary()
        logs = BackupLog.objects.order_by('-created_at')[:20]
        return render(request, 'backup_restore/dashboard_v7.html', {'config': config, 'logs': logs})

class ConfigureBackupView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def post(self, request):
        config = BackupConfiguration.get_solitary()
        config.auto_backup = request.POST.get('auto_backup') == 'on'
        config.frequency = request.POST.get('frequency')
        try:
            config.custom_days = int(request.POST.get('custom_days', 1))
        except ValueError:
            config.custom_days = 1
            
        try:
            config.retention_days = int(request.POST.get('retention_days', 30))
        except ValueError:
            config.retention_days = 30
            
        config.email_notifications = request.POST.get('email_notifications') == 'on'
        config.email_files_only = request.POST.get('email_files_only') == 'on'
        
        # Validate path roughly
        path = request.POST.get('backup_path', 'backups')
        config.backup_path = path
        
        config.save()
        messages.success(request, 'Backup configuration updated.')
        return redirect('backup_dashboard')

class TriggerBackupView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def post(self, request):
        backup_type = request.POST.get('backup_type', 'full')
        # Run in thread to not block response? 
         # For manual backup, user usually wants to see success message. 
        # But if project is huge, it will timeout.
        # Let's run synchronously for now, if it's too slow we can move to async.
        success, msg = BackupService.create_backup(backup_type=backup_type)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, f"Backup failed: {msg}")
        return redirect('backup_dashboard')

class BrowsePathView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def get(self, request):
        try:
            # Execute the browse_folder.py script
            script_path = os.path.join(os.path.dirname(__file__), 'browse_folder.py')
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True,
                check=True # Don't raise, check returncode
            )
            
            path = result.stdout.strip()
            if path:
                return JsonResponse({'path': path})
            else:
                return JsonResponse({'path': ''}) # User cancelled
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class DownloadBackupView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def get(self, request, log_id):
        try:
            log = BackupLog.objects.get(id=log_id)
            if os.path.exists(log.file_path):
                with open(log.file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/zip")
                    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(log.file_path)
                    return response
            else:
                messages.error(request, "File not found on server.")
        except Exception as e:
            messages.error(request, "Error retrieving file.")
        return redirect('backup_dashboard')

class RestoreBackupView(LoginRequiredMixin, SuperUserRequiredMixin, WaffleFlagMixin, View):
    def post(self, request):
        password = request.POST.get('password')
        if not request.user.check_password(password):
            messages.error(request, "Invalid password. Restore aborted.")
            return redirect('backup_dashboard')

        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            messages.error(request, "Please upload a backup file.")
            return redirect('backup_dashboard')

        # Save uploaded file temporarily
        temp_path = os.path.join(settings.BASE_DIR, 'temp_restore.zip')
        with open(temp_path, 'wb+') as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        # Trigger Restore Script
        try:
            # We call the batch script effectively detaching it
            # The script should kill this process
            # Pass DB_PASSWORD as env var if needed, or rely on pgpass/default
            
            db_settings = settings.DATABASES['default']
            
            env = os.environ.copy()
            env['DB_USER'] = db_settings['USER']
            env['PGPASSWORD'] = db_settings['PASSWORD']
            env['DB_NAME'] = db_settings['NAME']
            env['DB_HOST'] = db_settings['HOST']
            env['DB_PORT'] = str(db_settings['PORT'])

            restore_script = os.path.join(settings.BASE_DIR, 'restore_system.bat')
            
            # Start detached process
            subprocess.Popen(
                [restore_script, temp_path, str(settings.BASE_DIR)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=env
            )
            
            # We are expecting the server to die now.
            return render(request, 'backup_restore/restoring.html')
            
        except Exception as e:
            messages.error(request, f"Failed to start restore process: {e}")
            return redirect('backup_dashboard')
