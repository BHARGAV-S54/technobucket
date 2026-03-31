"""
WSGI config for technobucket project.
"""

import os
import django
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technobucket.settings")

django.setup()

from django.conf import settings
from django.core.wsgi import get_wsgi_application

if not settings.DEBUG:
    static_src = os.path.join(settings.BASE_DIR, "static")
    static_dst = settings.STATIC_ROOT

    if not os.path.exists(static_dst):
        os.makedirs(static_dst)

    for item in os.listdir(static_src):
        src_path = os.path.join(static_src, item)
        dst_path = os.path.join(static_dst, item)
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

application = get_wsgi_application()
