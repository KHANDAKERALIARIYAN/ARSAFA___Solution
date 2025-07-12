from django.core.management.base import BaseCommand
from lending.models import Lending
from invoices.models import POS
from customers.models import Customer
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Verify lending records and show which customers should be in the lending module'

    def handle(self, *args, **options):
        self.stdout.write('Verifying lending records...')
        
        # Get all customers with unpaid POS bills
        unpaid_customers = POS.objects.filter(status='unpaid').values('customer_name', 'contact_number').distinct()
        
        self.stdout.write(f'\nCustomers with unpaid POS bills (should be in lending module):')
        self.stdout.write('=' * 60)
        
        for customer_data in unpaid_customers:
            customer_name = customer_data['customer_name']
            contact_number = customer_data['contact_number']
            
            # Get total unpaid amount
            unpaid_total = POS.objects.filter(
                customer_name=customer_name,
                contact_number=contact_number,
                status='unpaid'
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Check if they have a lending record
            customer = Customer.objects.filter(name=customer_name, phone=contact_number).first()
            has_lending = Lending.objects.filter(customer=customer).exists() if customer else False
            
            status_icon = "✓" if has_lending else "✗"
            status_text = "HAS LENDING RECORD" if has_lending else "MISSING LENDING RECORD"
            
            self.stdout.write(f'{status_icon} {customer_name} ({contact_number})')
            self.stdout.write(f'    Unpaid Amount: ৳{unpaid_total}')
            self.stdout.write(f'    Status: {status_text}')
            self.stdout.write('')
        
        # Get all lending records
        lending_records = Lending.objects.all()
        
        self.stdout.write(f'\nCurrent lending records:')
        self.stdout.write('=' * 60)
        
        for lending in lending_records:
            customer = lending.customer
            
            # Check if customer has unpaid bills
            unpaid_pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone,
                status='unpaid'
            )
            
            has_unpaid = unpaid_pos_bills.exists()
            status_icon = "✓" if has_unpaid else "✗"
            status_text = "VALID" if has_unpaid else "INVALID (no unpaid bills)"
            
            self.stdout.write(f'{status_icon} {customer.name} ({customer.phone})')
            self.stdout.write(f'    Lending Amount: ৳{lending.amount}')
            self.stdout.write(f'    Status: {status_text}')
            self.stdout.write('')
        
        # Summary
        total_unpaid_customers = unpaid_customers.count()
        total_lending_records = lending_records.count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Customers with unpaid bills: {total_unpaid_customers}')
        self.stdout.write(f'Lending records: {total_lending_records}')
        
        # Check for mismatches
        customers_with_lending = set()
        for lending in lending_records:
            customers_with_lending.add((lending.customer.name, lending.customer.phone))
        
        customers_with_unpaid = set()
        for customer_data in unpaid_customers:
            customers_with_unpaid.add((customer_data['customer_name'], customer_data['contact_number']))
        
        missing_lending = customers_with_unpaid - customers_with_lending
        invalid_lending = customers_with_lending - customers_with_unpaid
        
        if missing_lending:
            self.stdout.write(f'\n⚠️  Customers missing lending records:')
            for name, phone in missing_lending:
                self.stdout.write(f'   - {name} ({phone})')
        
        if invalid_lending:
            self.stdout.write(f'\n⚠️  Invalid lending records (customers with no unpaid bills):')
            for name, phone in invalid_lending:
                self.stdout.write(f'   - {name} ({phone})')
        
        if not missing_lending and not invalid_lending:
            self.stdout.write(f'\n✅ All lending records are correct!') 