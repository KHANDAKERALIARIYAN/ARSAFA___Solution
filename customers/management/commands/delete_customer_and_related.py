from django.core.management.base import BaseCommand
from customers.models import Customer
from invoices.models import Invoice, InvoiceItem, POS, POSItem
from sales.models import Sale, SaleItem
from lending.models import Lending

class Command(BaseCommand):
    help = 'Delete a customer and all related data (invoices, POS, sales, lending) by customer ID.'

    def add_arguments(self, parser):
        parser.add_argument('--customer_id', type=int, required=True, help='ID of the customer to delete')

    def handle(self, *args, **options):
        customer_id = options['customer_id']
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Customer with ID {customer_id} does not exist.'))
            return

        self.stdout.write(f'Deleting all related data for customer: {customer.name} (ID: {customer.id})')

        # Delete InvoiceItems and Invoices
        invoices = Invoice.objects.filter(customer=customer)
        for invoice in invoices:
            InvoiceItem.objects.filter(invoice=invoice).delete()
            invoice.delete()
        self.stdout.write(f'Deleted {invoices.count()} invoices and their items.')

        # Delete POSItems and POS
        pos_list = POS.objects.filter(customer_name=customer.name, contact_number=customer.phone)
        for pos in pos_list:
            POSItem.objects.filter(pos=pos).delete()
            pos.delete()
        self.stdout.write(f'Deleted {pos_list.count()} POS records and their items.')

        # Delete SaleItems and Sales
        sales = Sale.objects.filter(customer=customer)
        for sale in sales:
            SaleItem.objects.filter(sale=sale).delete()
            sale.delete()
        self.stdout.write(f'Deleted {sales.count()} sales and their items.')

        # Delete Lending records
        lending_records = Lending.objects.filter(customer=customer)
        count_lending = lending_records.count()
        lending_records.delete()
        self.stdout.write(f'Deleted {count_lending} lending records.')

        # Finally, delete the customer
        customer.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted customer {customer.name} and all related data.')) 