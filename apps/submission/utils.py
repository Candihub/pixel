import re

from os import makedirs
from pathlib import Path

from django.conf import settings
from django.utils.translation import ugettext as _


def is_hidden_task(task_name):
    if not isinstance(task_name, str):
        raise ValueError(_("Task name should be a string"))
    if re.match('start|end|check', task_name):
        return True
    return False


def ensure_tree(relative_path, root=settings.MEDIA_ROOT, dry_run=False):
    """
    Ensure that the relative path tree exists and creates it if not. Note that
    if relative_path points to a directory only its parents directories will be
    created.

    Parameters
    ----------
    relative_path :  :obj:`Path`
        The relative Path to a file
    root : str, optional
        The reference root used to calculate the absolute path of the query
        file. The default root is the MEDIA_ROOT
    dry_run : bool, optional
        If True the relative path tree won't be created. Defaults to False.

    Returns
    -------
    Path
        The absolute Path calculated from root
    """

    absolute_path = Path(root) / relative_path
    if not absolute_path.parent.exists() and not dry_run:
        makedirs(absolute_path.parent)

    return absolute_path
