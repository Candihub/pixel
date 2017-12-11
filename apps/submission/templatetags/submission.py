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
def core_tasks(tasks):
    """Removes tasks from a task queryset if their class name contains:

    * check
    * start
    * end

    Returns: a filtered list of tasks
    """
    filtered = []
    for task in tasks:
        name = str(task).lower()
        if 'start' in name or \
                'end' in name or \
                'check' in name:
            continue
        filtered.append(task)
    return filtered
