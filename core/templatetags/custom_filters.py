from django import template

register = template.Library()


@register.filter
def dict_value(obj, key):
    """
    Safely get attribute value from an object using a string key.
    Example: {{ object|dict_value:"roll_number" }}
    """
    try:
        # Support for related fields (course.name etc)
        attrs = key.split('.')
        for attr in attrs:
            obj = getattr(obj, attr)
        return obj
    except Exception:
        return ""
