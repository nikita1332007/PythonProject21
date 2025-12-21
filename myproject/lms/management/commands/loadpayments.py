from django.core.management.base import BaseCommand
import json
import os
from myproject.users.models import Payment


class Command(BaseCommand):
    help = 'Load payments data from JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('lms', 'fixtures', 'payments.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
        for item in data:
            fields = item['fields']
            Payment.objects.update_or_create(
                pk=item['pk'],
                defaults=fields,
            )
        self.stdout.write(self.style.SUCCESS('Payments data loaded successfully'))