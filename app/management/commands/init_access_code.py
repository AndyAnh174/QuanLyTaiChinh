"""
Management command to initialize access code
Usage: python manage.py init_access_code [code]
"""
from django.core.management.base import BaseCommand
from app.models import AccessCode


class Command(BaseCommand):
    help = 'Initialize or update access code'

    def add_arguments(self, parser):
        parser.add_argument(
            'code',
            nargs='?',
            type=str,
            default='1234',
            help='Access code to set (default: 1234)'
        )

    def handle(self, *args, **options):
        code = options['code']
        AccessCode.set_code(code)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set access code to: {code}')
        )

