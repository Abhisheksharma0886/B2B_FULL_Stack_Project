from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create default Django Admin superuser (admin/admin123)'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f"Creating superuser: {username}...")
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role='admin',
                raw_password_view=password
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' successfully created."))
        else:
            admin_user = User.objects.get(username=username)
            admin_user.set_password(password)
            admin_user.email = email
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.role = 'admin'
            admin_user.raw_password_view = password
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' credentials updated/verified."))
