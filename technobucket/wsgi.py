import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technobucket.settings")

# Run migrations on cold start so /tmp/db.sqlite3 is always up to date.
# This is safe to call repeatedly (it's a no-op when nothing has changed).
import django
django.setup()

from django.conf import settings
db_name = str(settings.DATABASES["default"].get("NAME", ""))
from django.core.management import call_command
try:
    call_command("migrate", "--run-syncdb", verbosity=0)
except Exception:
    pass

application = get_wsgi_application()
