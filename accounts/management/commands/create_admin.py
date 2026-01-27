from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = "Create default admin user"

    def handle(self, *args, **kwargs):
        email = config("DJANGO_SUPERUSER_EMAIL")
        password = config("DJANGO_SUPERUSER_PASSWORD")

        # delete old admin if exists
        User.objects.filter(email=email).delete()

        User.objects.create_superuser(email=email, password=password)

        self.stdout.write(self.style.SUCCESS("Admin user created / updated"))
