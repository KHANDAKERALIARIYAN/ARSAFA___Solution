from django.core.management.base import BaseCommand
from django.db import transaction
from invoices.models import Invoice, InvoiceItem

class Command(BaseCommand):
    help = 'Deletes all invoice and invoice item records from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            help='Confirm that you want to delete all invoice data.',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                'This command will delete ALL invoices and their items. '
                'This action cannot be undone.'
            ))
            self.stdout.write(self.style.WARNING(
                'To proceed, run the command again with the --confirm flag.'
            ))
            return

        with transaction.atomic():
            invoice_item_count = InvoiceItem.objects.count()
            invoice_count = Invoice.objects.count()

            if invoice_item_count == 0 and invoice_count == 0:
                self.stdout.write(self.style.SUCCESS('There is no invoice data to delete.'))
                return

            # Delete items first to respect foreign key constraints
            items_deleted, _ = InvoiceItem.objects.all().delete()
            invoices_deleted, _ = Invoice.objects.all().delete()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully deleted {items_deleted} invoice items.'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Successfully deleted {invoices_deleted} invoices.'
            ))
            self.stdout.write(self.style.SUCCESS('All invoice data has been cleared.')) 