from django import template

register = template.Library()

@register.filter
def until(value, arg):
    try:
        return range(value, arg)
    except:
        return []

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except:
        return 0
