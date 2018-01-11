from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def filename(path):
    """Removes traceback lines from a string (if any). It has no effect when
    no 'Traceback' pattern has been found.

    Returns: raws before the 'Traceback' pattern
    """
    return Path(path).name
