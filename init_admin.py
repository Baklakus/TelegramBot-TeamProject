from django.contrib.auth.models import User
from django.db import IntegrityError

# Настройки
username = "admin"
email = "admin@example.com"
password = "admin123"

try:
    user, created = User.objects.update_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        }
    )

    user.set_password(password)
    user.save()

    if created:
        print(f"✅ Суперпользователь {username} создан")
    else:
        print(f"🔁 Суперпользователь {username} обновлён и сброшен пароль")

except IntegrityError as e:
    print(f"⚠ Ошибка при создании администратора: {e}")
