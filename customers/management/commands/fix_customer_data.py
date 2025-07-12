from django.core.management.base import BaseCommand
from customers.models import Customer
from invoices.models import POS
from lending.models import Lending
from sales.models import Sale
from decimal import Decimal
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Fix customer data by creating customers for existing POS records'

    def handle(self, *args, **options):
        self.stdout.write('Fixing customer data...')
        
        # Get all unique customer names and phone numbers from POS records
        pos_customers = POS.objects.values('customer_name', 'contact_number', 'email').distinct()
        
        created_count = 0
        updated_count = 0
        
        for pos_customer in pos_customers:
            customer_name = pos_customer['customer_name']
            contact_number = pos_customer['contact_number']
            email = pos_customer['email'] or ''
            
            # Try to find existing customer
            customer, created = Customer.objects.get_or_create(
                name=customer_name,
                phone=contact_number,
                defaults={'email': email}
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created customer: {customer_name} ({contact_number})')
            else:
                # Update email if it's different
                if email and customer.email != email:
                    customer.email = email
                    customer.save(update_fields=['email'])
                    updated_count += 1
                    self.stdout.write(f'Updated customer: {customer_name} ({contact_number})')
        
        # Update customer totals from POS records
        for customer in Customer.objects.all():
            pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone
            )
            
            total_sales = pos_bills.aggregate(total=Sum('total'))['total'] or 0
            customer.total_purchases = total_sales
            customer.outstanding_balance = total_sales
            
            # Get last purchase date
            last_pos = pos_bills.order_by('-date').first()
            if last_pos:
                customer.last_purchase = last_pos.date.date()
            
            customer.save()
        
        self.stdout.write(f'\nCreated {created_count} new customers')
        self.stdout.write(f'Updated {updated_count} existing customers')
        self.stdout.write('Customer data fix complete!') 