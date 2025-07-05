from django.core.management.base import BaseCommand
from customers.models import Customer


class Command(BaseCommand):
    help = 'Clear all customer data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all customer data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL customer data. Use --confirm to proceed.'
                )
            )
            return

        # Delete customers
        customers_count = Customer.objects.count()
        Customer.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {customers_count} customers.'
            )
        ) 