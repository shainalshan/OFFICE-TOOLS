from django import template

register = template.Library()

@register.filter
def is_eq(value, arg):
    """
    Returns True if value == arg.
    Usage: {% if value|is_eq:arg %}
    """
    return value == arg
