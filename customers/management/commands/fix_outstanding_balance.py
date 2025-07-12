from django.core.management.base import BaseCommand
from customers.models import Customer
from invoices.models import POS
from lending.models import Lending
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Fix outstanding balance calculations for all customers'

    def handle(self, *args, **options):
        self.stdout.write('Fixing outstanding balance calculations...')
        
        fixed_count = 0
        
        for customer in Customer.objects.all():
            # Get all POS bills for this customer
            all_pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone
            )
            
            # Get paid and unpaid POS bills
            paid_pos_bills = all_pos_bills.filter(status='paid')
            unpaid_pos_bills = all_pos_bills.filter(status='unpaid')
            
            # Calculate correct totals
            total_purchases = all_pos_bills.aggregate(total=Sum('total'))['total'] or 0
            outstanding_balance = unpaid_pos_bills.aggregate(total=Sum('total'))['total'] or 0
            
            # Check if values need updating
            if (customer.total_purchases != total_purchases or 
                customer.outstanding_balance != outstanding_balance):
                
                old_outstanding = customer.outstanding_balance
                old_total = customer.total_purchases
                
                customer.total_purchases = total_purchases
                customer.outstanding_balance = outstanding_balance
                customer.save()
                
                fixed_count += 1
                self.stdout.write(f'Fixed {customer.name}:')
                self.stdout.write(f'  Total Purchases: ৳{old_total} → ৳{total_purchases}')
                self.stdout.write(f'  Outstanding Balance: ৳{old_outstanding} → ৳{outstanding_balance}')
                self.stdout.write('')
        
        # Also fix lending records
        self.stdout.write('Fixing lending records...')
        lending_fixed = 0
        
        for lending in Lending.objects.all():
            customer = lending.customer
            
            # Get unpaid POS bills for this customer
            unpaid_pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone,
                status='unpaid'
            )
            
            correct_amount = unpaid_pos_bills.aggregate(total=Sum('total'))['total'] or 0
            
            if lending.amount != correct_amount:
                old_amount = lending.amount
                lending.amount = correct_amount
                lending.save()
                
                lending_fixed += 1
                self.stdout.write(f'Fixed lending for {customer.name}:')
                self.stdout.write(f'  Amount: ৳{old_amount} → ৳{correct_amount}')
                self.stdout.write('')
        
        self.stdout.write(f'\nFix complete!')
        self.stdout.write(f'Customers fixed: {fixed_count}')
        self.stdout.write(f'Lending records fixed: {lending_fixed}')
        
        # Show summary
        total_customers = Customer.objects.count()
        total_outstanding = Customer.objects.aggregate(total=Sum('outstanding_balance'))['total'] or 0
        total_lending = Lending.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        self.stdout.write(f'\nCurrent totals:')
        self.stdout.write(f'Total customers: {total_customers}')
        self.stdout.write(f'Total outstanding balance: ৳{total_outstanding}')
        self.stdout.write(f'Total lending amount: ৳{total_lending}')
        
        if total_outstanding == total_lending:
            self.stdout.write(f'✅ Outstanding balance matches lending amount!')
        else:
            self.stdout.write(f'⚠️  Outstanding balance ({total_outstanding}) does not match lending amount ({total_lending})') 