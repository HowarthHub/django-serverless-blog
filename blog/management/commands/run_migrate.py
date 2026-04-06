from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run migrations — used for Lambda invocation"

    def handle(self, *args, **options):
        self.stdout.write("Running migrations...")
        call_command("migrate", verbosity=1, stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS("Migrations complete!"))
