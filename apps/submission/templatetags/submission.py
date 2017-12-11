from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def hide_traceback(value):
    """Removes traceback lines from a string (if any). It has no effect when
    no 'Traceback' pattern has been found.

    Returns: raws before the 'Traceback' pattern
    """
    lines = value.split('\n')
    try:
        idx = lines.index('Traceback (most recent call last):')
    except ValueError:
        return value
    return '\n'.join(lines[:idx])


@register.filter
def hide_check_tasks(tasks):
    """Remove a task from a task queryset if it's class name starts by 'check'.

    Returns: a filtered list of tasks
    """
    return [t for t in tasks if 'check' not in str(t).lower()]
