from django.core.management.base import BaseCommand
from search_app.tasks import run_scheduler

class Command(BaseCommand):
    help = "Run YOLO image analysis scheduler"

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds")

    def handle(self, *args, **options):
        run_scheduler(interval_seconds=options["interval"])
