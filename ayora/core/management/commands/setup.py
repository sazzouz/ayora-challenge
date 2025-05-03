from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = """
    Master setup command that runs all necessary setup commands:
    - setup_periodic_tasks: Sets up Celery Beat periodic tasks
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting setup process...\n")

        try:
            self.stdout.write("Setting up periodic tasks...")
            call_command("setup_periodic_tasks")
            self.stdout.write(self.style.SUCCESS("\n✓ Periodic tasks configured\n"))

            self.stdout.write(self.style.SUCCESS("\nSetup completed successfully.\n"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Setup failed with error: {str(e)}\n"))
            raise
