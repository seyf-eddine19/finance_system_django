import os
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_system.settings')
django.setup()

User = get_user_model()

USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "admin"

if not User.objects.filter(username=USERNAME).exists():
    user = User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    user.set_password(PASSWORD)  # Ensure the password is hashed
    user.save()
    print("✅ Superuser created successfully!")
else:
    print("⚠️ Superuser already exists.")
