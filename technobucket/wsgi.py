"""
WSGI config for technobucket project.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technobucket.settings")

django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
