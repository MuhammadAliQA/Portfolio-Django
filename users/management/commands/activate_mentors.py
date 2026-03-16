from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Activate all mentor accounts."

    def handle(self, *args, **options):
        updated = User.objects.filter(role="mentor", is_active=False).update(is_active=True)
        self.stdout.write(self.style.SUCCESS(f"Activated {updated} mentor account(s)."))
