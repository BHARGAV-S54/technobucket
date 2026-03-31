"""
WSGI config for technobucket project.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technobucket.settings")

django.setup()

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

if not os.environ.get("DEBUG"):
    call_command("collectstatic", "--noinput", verbosity=0)

application = get_wsgi_application()
