from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def percent_diff(value, arg):
    """Calculate the percentage difference between two values."""
    try:
        return ((float(value) - float(arg)) / float(arg)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
