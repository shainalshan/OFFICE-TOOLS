from django.core.mail import get_connection, EmailMessage, send_mail
from django.conf import settings
from .models import EmailConfiguration

def send_dynamic_email(subject, message, recipient_list, from_email=None, html_message=None):
    """
    Sends an email using dynamic credentials from EmailConfiguration if available.
    Falls back to settings.py credentials if no config found.
    """
    config = EmailConfiguration.objects.first()
    
    if config:
        # Use dynamic config
        connection = get_connection(
            host=config.email_host,
            port=config.email_port,
            username=config.email_host_user,
            password=config.email_host_password,
            use_tls=config.email_use_tls
        )
        
        sender = from_email or config.default_from_email or config.email_host_user
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=sender,
            to=recipient_list,
            connection=connection
        )
        
        if html_message:
            email.content_subtype = "html"  # Main content is now text/html
            email.body = html_message
            
        return email.send()
    else:
        # Fallback to standard Django settings
        return send_mail(
            subject, 
            message, 
            from_email, 
            recipient_list, 
            html_message=html_message,
            fail_silently=False
        )
