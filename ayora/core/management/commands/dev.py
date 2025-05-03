from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Run in development mode.

    NOTE: this is not setup to efficiently handle changes, i.e. `collectstatic` will run on each change.
    """

    def handle(self, *args, **options):
        # essential setup
        management.call_command("makemigrations")
        management.call_command("migrate")
        # setup actions
        print("------------------ Setup --------------------\n")
        management.call_command("setup")
        print("Collecting static files...")
        management.call_command("collectstatic", "--noinput")
        print("---------------------------------------------\n")
        # run the server
        management.call_command("collectstatic", "--noinput")
        management.call_command("runserver", "0:8000", "--nostatic")
