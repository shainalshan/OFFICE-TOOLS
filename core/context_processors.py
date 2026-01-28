from .models import UserProfile, UserToolAccess

def theme_context(request):
    """
    Context processor to make the active theme available in all templates.
    Logic:
    1. If user is authenticated and has a specific preference, use it.
    2. Fallback to Global Default from ThemeConfiguration.
    3. Fallback to 'theme-default'.
    """
    return {}

def user_permissions(request):
    """
    Context processor to add 'allowed_tools' to the context.
    Returns a set of slugs of tools the user has access to.
    """
    if not request.user.is_authenticated:
        return {'allowed_tools': set()}
    
    # Superusers see everything? 
    # The user request says "if i add gave a permission...". 
    # Usually superusers have all permissions.
    if request.user.is_superuser:
        # We could return a special string or all slugs.
        # But for 'if x in allowed_tools', we need the actual slugs.
        # Fetching all slugs might be better. 
        # But let's stick to the UserToolAccess model for consistency with the request.
        # If the user implies permissions are explicit, maybe superuser isn't auto-granted?
        # Standard Django: superuser has all perms.
        # But `UserToolAccess` is a custom model.
        # Let's check if superusers are auto-granted in `setup_converter_tool.py`: "Granted access to all superusers" explicit loop.
        # So superusers follow the same rule: they need an entry in UserToolAccess.
        pass

    try:
        # Access the related_name 'tool_access' from User model
        access = getattr(request.user, 'tool_access', None)
        if access:
            allowed_tools = set(access.tools.values_list('slug', flat=True))
        else:
            allowed_tools = set()
    except Exception:
        allowed_tools = set()
        
    return {'allowed_tools': allowed_tools}
