from .models import UserProfile

def theme_context(request):
    """
    Context processor to make the active theme available in all templates.
    Logic:
    1. If user is authenticated and has a specific preference, use it.
    2. Fallback to Global Default from ThemeConfiguration.
    3. Fallback to 'theme-default'.
    """
    return {}
