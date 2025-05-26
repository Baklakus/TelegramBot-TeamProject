from django.contrib.auth.models import User
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'


def create_superuser(sender, **kwargs):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
