from django.core.management.base import BaseCommand
from django.utils import timezone
from invoices.models import POS, POSItem, Invoice, InvoiceItem
from customers.models import Customer
from inventory.models import Product
from sales.models import Sale, SaleItem
from lending.models import Lending
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test POS deletion and verify that all related modules are properly updated'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-pos',
            action='store_true',
            help='Create a test POS transaction to delete',
        )
        parser.add_argument(
            '--delete-pos',
            type=int,
            help='Delete a specific POS by ID and verify updates',
        )
        parser.add_argument(
            '--verify-deletion',
            action='store_true',
            help='Verify that deletion properly updates all modules',
        )

    def handle(self, *args, **options):
        if options['create_test_pos']:
            self.create_test_pos()
        elif options['delete_pos']:
            self.delete_pos_and_verify(options['delete_pos'])
        elif options['verify_deletion']:
            self.verify_deletion()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Use --create-test-pos to create test data, --delete-pos <id> to delete specific POS, or --verify-deletion to check deletion'
                )
            )

    def create_test_pos(self):
        """Create a test POS transaction for deletion testing"""
        
        # Check if we have products
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(
                self.style.ERROR('No products found. Please create some products first.')
            )
            return

        # Create test customer
        customer, created = Customer.objects.get_or_create(
            name='Test Customer',
            phone='01987654321',
            defaults={
                'email': 'test@gmail.com',
                'status': 'active',
                'total_purchases': Decimal('0.00'),
                'outstanding_balance': Decimal('0.00')
            }
        )

        # Create test POS
        last_pos = POS.objects.order_by('-pos_number').first()
        if last_pos:
            last_number = int(last_pos.pos_number.split('-')[1])
            pos_number = f'POS-{str(last_number + 1).zfill(3)}'
        else:
            pos_number = 'POS-001'

        pos = POS.objects.create(
            pos_number=pos_number,
            customer_name='Test Customer',
            contact_number='01987654321',
            email='test@gmail.com',
            status='paid',
            subtotal=Decimal('250.00'),
            total=Decimal('250.00')
        )

        # Create POS items
        product = products.first()
        POSItem.objects.create(
            pos=pos,
            product=product,
            quantity=2,
            unit_price=Decimal('100.00'),
            total=Decimal('200.00')
        )

        if products.count() > 1:
            product2 = products.last()
            POSItem.objects.create(
                pos=pos,
                product=product2,
                quantity=1,
                unit_price=Decimal('50.00'),
                total=Decimal('50.00')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Created test POS {pos.pos_number} for deletion testing'
            )
        )
        self.stdout.write(f'POS ID: {pos.id}')
        self.stdout.write(f'Customer: {customer.name}')
        self.stdout.write(f'Total: ৳{pos.total}')

    def delete_pos_and_verify(self, pos_id):
        """Delete a specific POS and verify all updates"""
        
        try:
            pos = POS.objects.get(id=pos_id)
        except POS.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'POS with ID {pos_id} not found.')
            )
            return

        # Store initial values for comparison
        customer = Customer.objects.filter(
            name=pos.customer_name,
            phone=pos.contact_number
        ).first()
        
        initial_customer_data = {
            'total_purchases': customer.total_purchases if customer else Decimal('0.00'),
            'outstanding_balance': customer.outstanding_balance if customer else Decimal('0.00'),
            'last_purchase': customer.last_purchase if customer else None
        }

        # Check related records before deletion
        related_invoice = pos.get_related_invoice()
        related_sale = pos.get_related_sale()
        related_lending = pos.get_related_lending()

        self.stdout.write(f'Before deletion:')
        self.stdout.write(f'  POS: {pos.pos_number} (৳{pos.total})')
        self.stdout.write(f'  Customer total purchases: ৳{initial_customer_data["total_purchases"]}')
        self.stdout.write(f'  Customer outstanding balance: ৳{initial_customer_data["outstanding_balance"]}')
        self.stdout.write(f'  Related invoice: {related_invoice.invoice_number if related_invoice else "None"}')
        self.stdout.write(f'  Related sale: {related_sale.id if related_sale else "None"}')
        self.stdout.write(f'  Related lending: {related_lending.id if related_lending else "None"}')

        # Delete the POS
        pos.delete()

        # Check updated values
        customer = Customer.objects.filter(
            name=pos.customer_name,
            phone=pos.contact_number
        ).first()

        self.stdout.write(f'\nAfter deletion:')
        if customer:
            self.stdout.write(f'  Customer total purchases: ৳{customer.total_purchases}')
            self.stdout.write(f'  Customer outstanding balance: ৳{customer.outstanding_balance}')
            self.stdout.write(f'  Customer last purchase: {customer.last_purchase}')
        else:
            self.stdout.write('  Customer not found (may have been deleted)')

        # Check if related records were deleted
        remaining_invoice = Invoice.objects.filter(invoice_number=pos.pos_number).first()
        remaining_sale = Sale.objects.filter(pos=pos).first()
        remaining_lending = Lending.objects.filter(
            customer=customer,
            notes__contains=f'POS {pos.pos_number} unpaid.'
        ).first() if customer else None

        self.stdout.write(f'  Related invoice deleted: {remaining_invoice is None}')
        self.stdout.write(f'  Related sale deleted: {remaining_sale is None}')
        self.stdout.write(f'  Related lending deleted: {remaining_lending is None}')

        # Verify the changes
        if customer:
            if pos.status == 'paid':
                expected_purchases = initial_customer_data['total_purchases'] - pos.total
                expected_balance = initial_customer_data['outstanding_balance'] + pos.total
            else:
                expected_purchases = initial_customer_data['total_purchases']
                expected_balance = initial_customer_data['outstanding_balance'] - pos.total

            if customer.total_purchases == expected_purchases:
                self.stdout.write(
                    self.style.SUCCESS('✓ Customer total purchases correctly reverted')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Customer total purchases not correctly reverted')
                )

            if customer.outstanding_balance == expected_balance:
                self.stdout.write(
                    self.style.SUCCESS('✓ Customer outstanding balance correctly reverted')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Customer outstanding balance not correctly reverted')
                )

    def verify_deletion(self):
        """Verify that deletion properly updates all modules"""
        
        # Check for any orphaned records
        orphaned_invoices = Invoice.objects.filter(invoice_number__startswith='POS-')
        orphaned_sales = Sale.objects.filter(pos__isnull=False)
        orphaned_lending = Lending.objects.filter(notes__contains='POS')

        self.stdout.write(f'Checking for orphaned records:')
        self.stdout.write(f'  Orphaned invoices: {orphaned_invoices.count()}')
        self.stdout.write(f'  Orphaned sales: {orphaned_sales.count()}')
        self.stdout.write(f'  Orphaned lending records: {orphaned_lending.count()}')

        if orphaned_invoices.exists():
            self.stdout.write(
                self.style.WARNING('Found orphaned invoices:')
            )
            for invoice in orphaned_invoices:
                self.stdout.write(f'    {invoice.invoice_number}')

        if orphaned_sales.exists():
            self.stdout.write(
                self.style.WARNING('Found orphaned sales:')
            )
            for sale in orphaned_sales:
                self.stdout.write(f'    Sale ID: {sale.id}')

        if orphaned_lending.exists():
            self.stdout.write(
                self.style.WARNING('Found orphaned lending records:')
            )
            for lending in orphaned_lending:
                self.stdout.write(f'    Lending ID: {lending.id} - {lending.notes}')

        if not any([orphaned_invoices.exists(), orphaned_sales.exists(), orphaned_lending.exists()]):
            self.stdout.write(
                self.style.SUCCESS('✓ No orphaned records found - deletion working correctly')
            ) 