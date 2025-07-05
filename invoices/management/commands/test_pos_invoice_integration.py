from django.core.management.base import BaseCommand
from django.utils import timezone
from invoices.models import POS, POSItem, Invoice, InvoiceItem
from customers.models import Customer
from inventory.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test POS to Invoice integration by creating sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create sample POS transactions to test integration',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify that POS transactions created corresponding invoices',
        )

    def handle(self, *args, **options):
        if options['create_sample']:
            self.create_sample_data()
        elif options['verify']:
            self.verify_integration()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Use --create-sample to create test data or --verify to check integration'
                )
            )

    def create_sample_data(self):
        """Create sample POS transactions to test integration"""
        
        # Check if we have products
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(
                self.style.ERROR('No products found. Please create some products first.')
            )
            return

        # Create sample customers
        customer1, created = Customer.objects.get_or_create(
            name='John Doe',
            phone='01712345678',
            defaults={
                'email': 'john@gmail.com',
                'status': 'active'
            }
        )
        
        customer2, created = Customer.objects.get_or_create(
            name='Jane Smith',
            phone='01887654321',
            defaults={
                'email': 'jane@gmail.com',
                'status': 'active'
            }
        )

        # Create sample POS transactions
        pos_data = [
            {
                'customer_name': 'John Doe',
                'contact_number': '01712345678',
                'email': 'john@gmail.com',
                'status': 'paid',
                'items': [
                    {'product': products.first(), 'quantity': 2, 'unit_price': Decimal('100.00')},
                    {'product': products.last(), 'quantity': 1, 'unit_price': Decimal('150.00')},
                ]
            },
            {
                'customer_name': 'Jane Smith',
                'contact_number': '01887654321',
                'email': 'jane@gmail.com',
                'status': 'unpaid',
                'items': [
                    {'product': products.first(), 'quantity': 1, 'unit_price': Decimal('100.00')},
                ]
            }
        ]

        for i, data in enumerate(pos_data):
            # Generate POS number
            last_pos = POS.objects.order_by('-pos_number').first()
            if last_pos:
                last_number = int(last_pos.pos_number.split('-')[1])
                pos_number = f'POS-{str(last_number + 1 + i).zfill(3)}'
            else:
                pos_number = f'POS-{str(i + 1).zfill(3)}'

            # Create POS
            pos = POS.objects.create(
                pos_number=pos_number,
                customer_name=data['customer_name'],
                contact_number=data['contact_number'],
                email=data['email'],
                status=data['status'],
                subtotal=sum(item['quantity'] * item['unit_price'] for item in data['items']),
                total=sum(item['quantity'] * item['unit_price'] for item in data['items'])
            )

            # Create POS items
            for item_data in data['items']:
                POSItem.objects.create(
                    pos=pos,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total=item_data['quantity'] * item_data['unit_price']
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created POS {pos.pos_number} for {data["customer_name"]} - Status: {data["status"]}'
                )
            )

    def verify_integration(self):
        """Verify that POS transactions created corresponding invoices"""
        
        pos_list = POS.objects.all()
        invoice_list = Invoice.objects.all()
        
        self.stdout.write(f'Found {pos_list.count()} POS transactions')
        self.stdout.write(f'Found {invoice_list.count()} invoices')
        
        # Check for POS-generated invoices
        pos_generated_invoices = Invoice.objects.filter(invoice_number__startswith='POS-')
        self.stdout.write(f'Found {pos_generated_invoices.count()} POS-generated invoices')
        
        # Verify each POS has corresponding invoice
        for pos in pos_list:
            invoice = Invoice.objects.filter(invoice_number=pos.pos_number).first()
            if invoice:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ POS {pos.pos_number} -> Invoice {invoice.invoice_number} (Status: {invoice.status})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ POS {pos.pos_number} has no corresponding invoice!'
                    )
                )
        
        # Check invoice items
        for invoice in pos_generated_invoices:
            pos = POS.objects.filter(pos_number=invoice.invoice_number).first()
            if pos:
                pos_items_count = pos.items.count()
                invoice_items_count = invoice.items.count()
                
                if pos_items_count == invoice_items_count:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Invoice {invoice.invoice_number} has {invoice_items_count} items (matches POS)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Invoice {invoice.invoice_number} has {invoice_items_count} items but POS has {pos_items_count} items'
                        )
                    ) 