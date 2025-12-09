from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='split')
def split(value, key):
    """
    Returns the value split by key.
    """
    return value.split(key)
