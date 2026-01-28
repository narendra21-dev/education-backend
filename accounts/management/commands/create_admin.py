from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update default admin user"

    def handle(self, *args, **kwargs):
        email = config("DJANGO_SUPERUSER_EMAIL", default=None)
        password = config("DJANGO_SUPERUSER_PASSWORD", default=None)

        if not email or not password:
            self.stdout.write(
                self.style.ERROR("Admin credentials not found in environment variables")
            )
            return

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": "admin"},
        )

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS("Admin user created / updated successfully")
        )
