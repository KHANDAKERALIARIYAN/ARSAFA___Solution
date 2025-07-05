# type: ignore[import-unresolved]
from django.db import models
from customers.models import Customer
from inventory.models import Product
from django.utils import timezone

class POS(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    pos_number = models.CharField(max_length=20, unique=True)  # POS-001 format
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pos_number

    def save(self, *args, **kwargs):
        self.total = self.subtotal - self.discount
        super().save(*args, **kwargs)

    def get_related_invoice(self):
        """Get the related invoice for this POS"""
        from invoices.models import Invoice
        return Invoice.objects.filter(invoice_number=self.pos_number).first()

    def get_related_sale(self):
        """Get the related sale for this POS"""
        from sales.models import Sale
        return Sale.objects.filter(pos=self).first()

    def get_related_lending(self):
        """Get the related lending record for this POS"""
        if self.status == 'unpaid':
            customer = Customer.objects.filter(
                name=self.customer_name,
                phone=self.contact_number
            ).first()
            if customer:
                from lending.models import Lending
                return Lending.objects.filter(
                    customer=customer,
                    status='active',
                    notes__contains=f'POS {self.pos_number} unpaid.'
                ).first()
        return None

    class Meta:
        ordering = ['-date']
        verbose_name = 'POS'
        verbose_name_plural = 'POS'

class POSItem(models.Model):
    pos = models.ForeignKey(POS, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.pos.pos_number}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)  # INV-001 format
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

    def is_pos_generated(self):
        """Check if this invoice was generated from a POS transaction"""
        return self.invoice_number.startswith('POS-')
    
    def get_pos_reference(self):
        """Get the POS reference if this invoice was generated from POS"""
        if self.is_pos_generated():
            return self.invoice_number
        return None

    class Meta:
        ordering = ['-date']

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs) 