from django.core.cache import cache
from .models import FeatureFlag

def is_feature_enabled(feature_name, default=True):
    """
    Checks if a feature is enabled.
    """
    # Try to get from cache first to avoid DB hits on every check
    cache_key = f"feature_flag_{feature_name}"
    is_active = cache.get(cache_key)

    if is_active is not None:
        return is_active

    try:
        flag = FeatureFlag.objects.get(name=feature_name)
        is_active = flag.is_active
    except FeatureFlag.DoesNotExist:
        # If flag doesn't exist, we respect the default
        # Ideally, we auto-create it or just log a warning? 
        # For now, just return default.
        is_active = default
    
    # Cache for 5 minutes
    cache.set(cache_key, is_active, timeout=300)
    
    return is_active

def clear_feature_cache(feature_name):
    cache.delete(f"feature_flag_{feature_name}")
