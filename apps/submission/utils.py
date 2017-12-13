import re

from django.utils.translation import ugettext as _


def is_hidden_task(task_name):
    if not isinstance(task_name, str):
        raise ValueError(_("Task name should be a string"))
    if re.match('start|end|check', task_name):
        return True
    return False
