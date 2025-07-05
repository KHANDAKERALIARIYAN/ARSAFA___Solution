from django.core.management.base import BaseCommand
from sales.models import Sale, SaleItem


class Command(BaseCommand):
    help = 'Clear all sales data including sales and sale items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all sales data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL sales data. Use --confirm to proceed.'
                )
            )
            return

        # Delete sale items first (due to foreign key constraints)
        sale_items_count = SaleItem.objects.count()
        SaleItem.objects.all().delete()
        
        # Delete sales
        sales_count = Sale.objects.count()
        Sale.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {sales_count} sales and {sale_items_count} sale items.'
            )
        ) 