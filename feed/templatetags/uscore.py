from django import template

register = template.Library()

@register.simple_tag
def get(dictionary, key):
    return getattr(dictionary, key)