import os
import sys
import django
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technobucket.settings")
django.setup()

def create_admin():
    User = get_user_model()
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists.")
        return

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Successfully created superuser: {username}")

if __name__ == "__main__":
    create_admin()
