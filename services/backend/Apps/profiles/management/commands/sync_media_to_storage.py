from pathlib import Path

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Copy files from MEDIA_ROOT into the configured default storage.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without writing to storage.',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Accepted for non-interactive deploy scripts.',
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stdout.write(self.style.WARNING(f'MEDIA_ROOT does not exist: {media_root}'))
            return

        uploaded = 0
        skipped = 0
        dry_run = options['dry_run']

        for path in media_root.rglob('*'):
            if not path.is_file():
                continue

            name = path.relative_to(media_root).as_posix()
            if default_storage.exists(name):
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f'Would upload {name}')
                uploaded += 1
                continue

            with path.open('rb') as file_obj:
                default_storage.save(name, File(file_obj))
            uploaded += 1
            self.stdout.write(f'Uploaded {name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Media sync complete. Uploaded: {uploaded}. Skipped existing: {skipped}.'
            )
        )
