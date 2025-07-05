from django.core.management.base import BaseCommand
from sales.models import Sale, SaleItem
from invoices.models import Invoice, InvoiceItem, POS, POSItem
from customers.models import Customer


class Command(BaseCommand):
    help = 'Clear all sales, invoice, and customer data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL sales, invoice, and customer data. Use --confirm to proceed.'
                )
            )
            return

        # Get counts before deletion
        sale_items_count = SaleItem.objects.count()
        sales_count = Sale.objects.count()
        invoice_items_count = InvoiceItem.objects.count()
        invoices_count = Invoice.objects.count()
        pos_items_count = POSItem.objects.count()
        pos_count = POS.objects.count()
        customers_count = Customer.objects.count()

        # Delete in order to respect foreign key constraints
        # 1. Delete sale items first
        SaleItem.objects.all().delete()
        
        # 2. Delete POS items
        POSItem.objects.all().delete()
        
        # 3. Delete invoice items
        InvoiceItem.objects.all().delete()
        
        # 4. Delete sales
        Sale.objects.all().delete()
        
        # 5. Delete invoices
        Invoice.objects.all().delete()
        
        # 6. Delete POS records
        POS.objects.all().delete()
        
        # 7. Delete customers
        Customer.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted all data:\n'
                f'- {sales_count} sales and {sale_items_count} sale items\n'
                f'- {invoices_count} invoices and {invoice_items_count} invoice items\n'
                f'- {pos_count} POS records and {pos_items_count} POS items\n'
                f'- {customers_count} customers'
            )
        ) 