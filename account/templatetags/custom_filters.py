from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """Check if value ends with arg."""
    return str(value).endswith(str(arg))