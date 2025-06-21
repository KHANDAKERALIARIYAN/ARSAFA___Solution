from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Sale, SaleItem
from inventory.models import Product
from customers.models import Customer

class SalesReportTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@example.com",
            phone="1234567890"
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name="Test Product 1",
            category="snacks",
            quantity=50,
            unit_price=100.00,
            buying_price=80.00
        )
        self.product2 = Product.objects.create(
            name="Test Product 2", 
            category="beverages",
            quantity=30,
            unit_price=200.00,
            buying_price=150.00
        )
        
        # Create test sales for different days
        today = timezone.now().date()
        
        # Sale for today
        sale1 = Sale.objects.create(
            customer=self.customer,
            total_amount=300.00,
            date=timezone.now()
        )
        SaleItem.objects.create(
            sale=sale1,
            product=self.product1,
            quantity=2,
            unit_price=100.00
        )
        SaleItem.objects.create(
            sale=sale1,
            product=self.product2,
            quantity=1,
            unit_price=100.00
        )
        
        # Sale for yesterday
        sale2 = Sale.objects.create(
            customer=self.customer,
            total_amount=200.00,
            date=timezone.now() - timedelta(days=1)
        )
        SaleItem.objects.create(
            sale=sale2,
            product=self.product1,
            quantity=2,
            unit_price=100.00
        )

    def test_sales_report_view(self):
        """Test that the sales report view loads correctly"""
        response = self.client.get(reverse('sales_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sales/sales_report.html')
        
        # Check that context contains expected data
        context = response.context
        self.assertIn('total_sales', context)
        self.assertIn('total_orders', context)
        self.assertIn('daily_labels', context)
        self.assertIn('daily_totals', context)
        self.assertIn('product_names', context)
        self.assertIn('product_units', context)
        
        # Check that daily labels contain all 7 days of the week
        daily_labels = context['daily_labels']
        self.assertIn('"Mon"', daily_labels)
        self.assertIn('"Tue"', daily_labels)
        self.assertIn('"Wed"', daily_labels)
        self.assertIn('"Thu"', daily_labels)
        self.assertIn('"Fri"', daily_labels)
        self.assertIn('"Sat"', daily_labels)
        self.assertIn('"Sun"', daily_labels)

    def test_weekly_sales_data(self):
        """Test that weekly sales data is calculated correctly"""
        response = self.client.get(reverse('sales_report'))
        context = response.context
        
        # Check that we have sales data for the week
        daily_totals = context['daily_totals']
        self.assertIsInstance(daily_totals, str)
        
        # The data should be a JSON array with 7 values (one for each day)
        import json
        totals = json.loads(daily_totals)
        self.assertEqual(len(totals), 7)

    def test_top_products_data(self):
        """Test that top products data is calculated correctly"""
        response = self.client.get(reverse('sales_report'))
        context = response.context
        
        # Check that we have top products data
        self.assertIn('top_products', context)
        self.assertIn('product_names', context)
        self.assertIn('product_units', context)
        
        # Check that product names and units are JSON arrays
        product_names = context['product_names']
        product_units = context['product_units']
        
        import json
        names = json.loads(product_names)
        units = json.loads(product_units)
        
        # Should have the same number of products and units
        self.assertEqual(len(names), len(units))
        
        # Should have at least our test products
        self.assertIn('Test Product 1', names)
        self.assertIn('Test Product 2', names) 