import os
import sys

base_dir = r"c:\Users\sanab\Downloads\Techno"
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexiolabs.settings")

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

c = Client()
try:
    resp = c.get("/admin-login/")
    print("Login Status:", resp.status_code)
    
    user, _ = User.objects.get_or_create(username="admin")
    c.force_login(user)
    
    print("Testing /admin-dashboard/ ...")
    resp2 = c.get("/admin-dashboard/")
    print("Dashboard Status:", resp2.status_code)
    if resp2.status_code == 500:
        print(resp2.content.decode("utf-8", errors="ignore"))
    elif resp2.status_code == 200:
        print("Success! Head of content:", resp2.content.decode("utf-8", errors="ignore")[:300])
    else:
        print("Empty or redirect content:", resp2.content)
except Exception as e:
    import traceback
    traceback.print_exc()
