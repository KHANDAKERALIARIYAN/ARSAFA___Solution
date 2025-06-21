from django.core.management.base import BaseCommand
from sales.models import Sale, SaleItem

class Command(BaseCommand):
    help = 'Delete all sales data from the database'

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
                    'This will delete ALL sales data including Sale and SaleItem records.\n'
                    'To proceed, run: python manage.py clear_sales_data --confirm'
                )
            )
            return

        # Get counts before deletion
        sale_count = Sale.objects.count()
        sale_item_count = SaleItem.objects.count()

        if sale_count == 0 and sale_item_count == 0:
            self.stdout.write(
                self.style.WARNING('No sales data found to delete.')
            )
            return

        # Delete all sale items first (due to foreign key relationship)
        SaleItem.objects.all().delete()
        self.stdout.write(f"Deleted {sale_item_count} sale items")

        # Delete all sales
        Sale.objects.all().delete()
        self.stdout.write(f"Deleted {sale_count} sales")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted all sales data!\n'
                f'Total records deleted: {sale_count + sale_item_count}'
            )
        ) 