"""
WSGI config for pixel project.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pixel.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

from configurations.wsgi import get_wsgi_application  # noqa

application = get_wsgi_application()
