from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def hide_traceback(value):
    lines = value.split('\n')
    try:
        idx = lines.index('Traceback (most recent call last):')
    except ValueError:
        return value
    return lines[:idx][0]


@register.filter
def hide_check_tasks(tasks):
    return [t for t in tasks if 'check' not in str(t).lower()]
