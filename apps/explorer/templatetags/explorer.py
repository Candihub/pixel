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
