import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def highlight(text, word):
    if len(word) == 0:
        return mark_safe(text)

    return mark_safe(
        text.replace(word, '<span class="highlight">{}</span>'.format(word))
    )


@register.filter
@stringfilter
def highlight_terms(text, words):
    if not words:
        return mark_safe(text)

    return mark_safe(
        re.sub(
            r'({})'.format('|'.join(words)),
            '<span class="highlight">\\1</span>',
            text,
            flags=re.IGNORECASE
        )
    )


@register.filter
@stringfilter
def concat(left, right):
    return str(left) + str(right)
