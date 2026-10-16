import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial site superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")
        email = os.environ.get("ADMIN_EMAIL", "").strip()

        if not username or not password:
            raise CommandError(
                "Set ADMIN_USERNAME and ADMIN_PASSWORD in the deployment environment "
                "before running bootstrap_admin. Do not put passwords in source code."
            )
        if len(password) < 14:
            raise CommandError("ADMIN_PASSWORD must be at least 14 characters long.")

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise CommandError(
                f"The account '{username}' already exists. Use "
                "'python manage.py changepassword " + username + "' to change its password."
            )

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{user.get_username()}' created successfully. "
            "Sign in at /admin/ and remove or rotate the deployment password after use."
        ))
