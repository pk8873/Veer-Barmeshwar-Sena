import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Create the initial Django admin from temporary deployment environment variables."""

    help = "Create an initial superuser when DJANGO_ADMIN_* variables are configured."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME", "").strip()
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "").strip()

        if not username and not password and not email:
            self.stdout.write("Admin bootstrap skipped (no DJANGO_ADMIN_* variables configured).")
            return

        if not username or not password:
            raise CommandError(
                "Set both DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD, or remove "
                "all DJANGO_ADMIN_* variables to skip admin bootstrap."
            )

        User = get_user_model()
        if User.objects.filter(**{User.USERNAME_FIELD: username}).exists():
            self.stdout.write(
                self.style.WARNING(
                    "Admin bootstrap did not change an existing account. "
                    "Choose a new username for the initial setup, or use Django's "
                    "password-reset procedure for the existing account."
                )
            )
            return

        user = User.objects.create_superuser(
            **{
                User.USERNAME_FIELD: username,
                "email": email,
                "password": password,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Initial admin account created: {user.get_username()}"))
