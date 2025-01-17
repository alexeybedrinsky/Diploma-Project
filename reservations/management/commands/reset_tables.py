from django.core.management.base import BaseCommand
from tables.models import Table


class Command(BaseCommand):
    help = 'Сбрасывает все столы в статус "доступен"'

    def handle(self, *args, **options):
        updated = Table.objects.update(is_available=True)
        self.stdout.write(self.style.SUCCESS(f"Успешно сброшено {updated} столов"))
