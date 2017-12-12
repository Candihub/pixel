import re


def is_hidden_task(task_name):
    if re.match('start|end|check', task_name):
        return True
    return False
