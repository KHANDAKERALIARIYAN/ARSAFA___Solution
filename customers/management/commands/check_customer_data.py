from django.core.management.base import BaseCommand
from customers.models import Customer
from invoices.models import POS
from lending.models import Lending
from sales.models import Sale

class Command(BaseCommand):
    help = 'Check and fix customer data issues'

    def handle(self, *args, **options):
        self.stdout.write('Checking customer data...')
        
        # Check POS records
        pos_count = POS.objects.count()
        self.stdout.write(f'POS records: {pos_count}')
        
        # Check customers
        customer_count = Customer.objects.count()
        self.stdout.write(f'Customers: {customer_count}')
        
        # Check lendings
        lending_count = Lending.objects.count()
        self.stdout.write(f'Lending records: {lending_count}')
        
        # Check sales
        sale_count = Sale.objects.count()
        self.stdout.write(f'Sales records: {sale_count}')
        
        # Show some sample data
        if customer_count > 0:
            self.stdout.write('\nSample customers:')
            for customer in Customer.objects.all()[:3]:
                self.stdout.write(f'  - {customer.name} ({customer.phone})')
        
        if pos_count > 0:
            self.stdout.write('\nSample POS records:')
            for pos in POS.objects.all()[:3]:
                self.stdout.write(f'  - {pos.pos_number} for {pos.customer_name} ({pos.contact_number}) - ৳{pos.total}')
        
        if lending_count > 0:
            self.stdout.write('\nSample lending records:')
            for lending in Lending.objects.all()[:3]:
                self.stdout.write(f'  - {lending.customer.name} - ৳{lending.amount} ({lending.status})')
        
        self.stdout.write('\nData check complete!') 