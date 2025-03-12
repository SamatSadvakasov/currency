
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update Parsing"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Successfully start running an updater')
        )
        self.stdout.write(
                self.style.SUCCESS('Successfully end running an updater')
        )
