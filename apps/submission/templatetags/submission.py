from django import template
from django.template.defaultfilters import stringfilter
from viewflow.activation import STATUS

from ..flows import SubmissionFlow
from ..utils import is_hidden_task

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
        if is_hidden_task(str(task.flow_task).lower()):
            continue
        filtered.append(task)
    return filtered


@register.simple_tag
def submission_ratio(process):
    """Calculates achived tasks ratio for a given submission process

    Returns: an integer in [0;100]
    """
    total = len(SubmissionFlow()._meta.nodes())
    done = process.task_set\
        .filter(status=STATUS.DONE)\
        .order_by('flow_task')\
        .distinct('flow_task')\
        .count()
    return int(done/total * 100.)
