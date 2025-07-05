from django.core.management.base import BaseCommand
from invoices.models import Invoice, InvoiceItem, POS, POSItem


class Command(BaseCommand):
    help = 'Clear all invoice data including invoices, invoice items, POS, and POS items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all invoice data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL invoice data. Use --confirm to proceed.'
                )
            )
            return

        # Delete invoice items first (due to foreign key constraints)
        invoice_items_count = InvoiceItem.objects.count()
        InvoiceItem.objects.all().delete()
        
        # Delete POS items first (due to foreign key constraints)
        pos_items_count = POSItem.objects.count()
        POSItem.objects.all().delete()
        
        # Delete invoices
        invoices_count = Invoice.objects.count()
        Invoice.objects.all().delete()
        
        # Delete POS records
        pos_count = POS.objects.count()
        POS.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {invoices_count} invoices, {invoice_items_count} invoice items, '
                f'{pos_count} POS records, and {pos_items_count} POS items.'
            )
        ) 