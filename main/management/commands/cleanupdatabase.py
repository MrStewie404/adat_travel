from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from main.models.clients.guest_form.guest_form_link import GuestFormLink


class Command(BaseCommand):
    help = 'Cleans up database from old data (expected to be called on server in automated fashion).'

    def handle(self, *args, **options):
        self.cleanup_guest_links()

    def cleanup_guest_links(self):
        max_age = timedelta(days=7)
        min_date_time = timezone.now() - max_age
        old_guest_links = GuestFormLink.objects.filter(created_at__lt=min_date_time)
        if old_guest_links.exists():
            count = old_guest_links.count()
            old_guest_links.delete()
            self.stdout.write(f"Deleted {count} old guest link(s).")
        else:
            self.stdout.write("Not found old guest links to delete.")
