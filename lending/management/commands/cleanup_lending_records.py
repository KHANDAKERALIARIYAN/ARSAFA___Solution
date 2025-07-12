from django.core.management.base import BaseCommand
from lending.models import Lending
from invoices.models import POS
from customers.models import Customer
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Clean up lending records to ensure only customers with unpaid POS bills are in lending module'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up lending records...')
        
        # Get all lending records
        lending_records = Lending.objects.all()
        deleted_count = 0
        kept_count = 0
        
        for lending in lending_records:
            customer = lending.customer
            
            # Check if this customer has any unpaid POS bills
            unpaid_pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone,
                status='unpaid'
            )
            
            if unpaid_pos_bills.exists():
                # Customer has unpaid bills, keep the lending record
                kept_count += 1
                self.stdout.write(f'✓ Kept lending record for {customer.name} (has unpaid bills)')
            else:
                # Customer has no unpaid bills, delete the lending record
                lending.delete()
                deleted_count += 1
                self.stdout.write(f'✗ Deleted lending record for {customer.name} (no unpaid bills)')
        
        self.stdout.write(f'\nCleanup complete!')
        self.stdout.write(f'Kept: {kept_count} lending records')
        self.stdout.write(f'Deleted: {deleted_count} lending records')
        
        # Show summary of current state
        self.stdout.write(f'\nCurrent state:')
        self.stdout.write(f'Total lending records: {Lending.objects.count()}')
        self.stdout.write(f'Total customers with unpaid bills: {POS.objects.filter(status="unpaid").values("customer_name", "contact_number").distinct().count()}')
        
        # Show customers who should be in lending module
        unpaid_customers = POS.objects.filter(status='unpaid').values('customer_name', 'contact_number').distinct()
        self.stdout.write(f'\nCustomers with unpaid bills:')
        for customer_data in unpaid_customers:
            customer_name = customer_data['customer_name']
            contact_number = customer_data['contact_number']
            unpaid_total = POS.objects.filter(
                customer_name=customer_name,
                contact_number=contact_number,
                status='unpaid'
            ).aggregate(total=Sum('total'))['total'] or 0
            
            self.stdout.write(f'  - {customer_name} ({contact_number}): ৳{unpaid_total}') 