from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def filename(path):
    """Removes parent path from a relative or absolute filename

    Returns: the filename
    """
    return Path(path).name
