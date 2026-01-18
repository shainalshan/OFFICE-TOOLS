from .models import ThemeConfiguration, UserProfile

def theme_context(request):
    """
    Context processor to make the active theme available in all templates.
    Logic:
    1. If user is authenticated and has a specific preference, use it.
    2. Fallback to Global Default from ThemeConfiguration.
    3. Fallback to 'theme-default'.
    """
    active_theme = 'theme-default'
    
    # Check Global Config first (cached logic could be added here later)
    try:
        global_config = ThemeConfiguration.objects.first()
        if global_config:
            active_theme = global_config.global_theme
    except Exception:
        pass # Fallback to default if DB issue

    # Default to Global, then override with User preference
    if request.user.is_authenticated:
        try:
            # Need to access profile safely
            if hasattr(request.user, 'profile') and request.user.profile.theme_preference:
                active_theme = request.user.profile.theme_preference
        except UserProfile.DoesNotExist:
            pass
            
    return {'active_theme': active_theme}
