from django.contrib.auth.models import User

username = "admin"
email = "admin@example.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Администратор создан: {username} / {password}")
else:
    print("ℹ Администратор уже существует — пропуск")