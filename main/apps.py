from django.apps import AppConfig
from django.db.models.signals import post_migrate

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django.contrib.auth.models import Group
        def create_roles(sender, **kwargs):
            Group.objects.get_or_create(name='Администратор')
            Group.objects.get_or_create(name='Ведущий')

        post_migrate.connect(create_roles, sender=self)