# type: ignore[import-unresolved]
"""
Point of Sale (POS) and Invoice Models for ARSAFA ERP System

This module defines the data models for managing sales transactions in the
Point of Sale system and traditional invoice system. It includes models for:
- POS transactions with real-time processing
- Traditional invoice system for deferred payments
- Related items for both systems

The models are designed to handle various business scenarios including:
- Real-time sales processing with immediate payment
- Deferred payment invoices with due dates
- Item-level tracking for inventory management
- Customer relationship management through transaction history

Author: ARSAFA Development Team
Version: 1.0
"""

# Import required Django modules and external models
from django.db import models
from customers.models import Customer
from inventory.models import Product
from django.utils import timezone

class POS(models.Model):
    """
    Point of Sale Transaction Model
    
    Represents a real-time sales transaction processed at the point of sale.
    This model captures all the details of a sale including customer information,
    items purchased, pricing, discounts, and payment status.
    
    Key Features:
    - Real-time transaction processing
    - Immediate payment handling
    - Discount application
    - Inventory tracking through POS items
    - Customer information storage
    """
    
    # Status choices for the POS transaction
    # 'paid' - Transaction has been completed with payment received
    # 'unpaid' - Transaction is pending payment or on credit
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    # Unique identifier for the POS transaction in POS-XXX format
    # Automatically generated to ensure uniqueness across all transactions
    pos_number = models.CharField(max_length=20, unique=True)  # POS-001 format
    
    # Customer information captured at the time of transaction
    # This allows for quick processing without requiring customer lookup
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # Transaction timestamp with automatic default to current time
    # Useful for reporting and analytics by date/time periods
    date = models.DateTimeField(default=timezone.now)
    
    # Financial fields for tracking transaction amounts
    # Subtotal: Sum of all item prices before discount
    # Discount: Amount deducted from subtotal
    # Total: Final amount after discount (subtotal - discount)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Current status of the transaction (paid/unpaid)
    # Controls business logic and UI behavior
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    
    # Audit fields for tracking creation and modification times
    # Useful for reporting, debugging, and data integrity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the POS transaction
        
        Returns the POS number for easy identification in admin interface
        and debugging output.
        """
        return self.pos_number

    def save(self, *args, **kwargs):
        """
        Custom save method to calculate total before saving
        
        This method ensures that the total amount is always correctly calculated
        as (subtotal - discount) before the record is saved to the database.
        This maintains data integrity and prevents calculation errors.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Note:
            Always call super().save() to ensure Django's default save behavior
        """
        # Calculate total amount based on subtotal and discount before saving
        # This ensures data consistency and prevents calculation errors
        self.total = self.subtotal - self.discount
        super().save(*args, **kwargs)
     
    def clean(self):
        """
        Model-level validation to ensure data integrity
        
        This method performs business rule validation that cannot be handled
        by standard Django field validators. It prevents invalid states such as
        marking a transaction as 'paid' when the total amount is zero or negative.
        
        Raises:
            ValidationError: When attempting to mark a zero/negative amount
                           transaction as 'paid'
        """
        # Model-level validation to ensure data integrity
        from django.core.exceptions import ValidationError
        # Prevent paid status for zero or negative total amounts
        # Business rule: Cannot mark as paid if there's nothing to pay
        if self.status == 'paid' and self.total <= 0:
            raise ValidationError("Cannot mark as paid for a transaction with zero or negative total amount.")
        super().clean()

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
   """
   Individual Item in a Point of Sale Transaction
   
   Represents a single product purchased in a POS transaction. Each POS
   transaction can have multiple items, and this model tracks the specific
   details of each item including quantity, price, and total amount.
   
   Relationship:
   - Belongs to one POS transaction (ForeignKey)
   - References one Product (ForeignKey)
   """
   
   # Reference to the parent POS transaction
   # Enables cascading deletion - if POS is deleted, all items are deleted
   pos = models.ForeignKey(POS, related_name='items', on_delete=models.CASCADE)
   
   # Reference to the product being sold
   # SET_NULL allows keeping transaction records even if product is deleted
   product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
   
   # Quantity of the product purchased
   # PositiveIntegerField ensures only positive quantities
   quantity = models.PositiveIntegerField()
   
   # Price per unit at the time of sale
   # Stored separately from product price to maintain historical accuracy
   unit_price = models.DecimalField(max_digits=10, decimal_places=2)
   
   # Total amount for this line item (quantity * unit_price)
   # Calculated and stored for performance and accuracy
   total = models.DecimalField(max_digits=10, decimal_places=2)

   def __str__(self):
       """
       String representation of the POS item
       
       Returns a descriptive string with product name and POS number for
       easy identification in admin interface and debugging output.
       """
       return f"{self.product.name} - {self.pos.pos_number}"

   def save(self, *args, **kwargs):
       """
       Custom save method to calculate total before saving
       
       This method ensures that the total amount for the item is always
       correctly calculated as (quantity * unit_price) before saving.
       
       Args:
           *args: Variable length argument list
           **kwargs: Arbitrary keyword arguments
       """
       # Calculate total amount for this line item before saving
       # This ensures data consistency and prevents calculation errors
       self.total = self.quantity * self.unit_price
       super().save(*args, **kwargs)

class Invoice(models.Model):
   """
   Traditional Invoice Model for Deferred Payment Transactions
   
   Represents a formal invoice for transactions where payment is deferred.
   This model is used for business-to-business transactions or customer
   accounts where payment is not made immediately at the time of sale.
   
   Key Features:
   - Due date tracking for payment terms
   - Customer account integration
   - Status tracking (paid/unpaid/overdue)
   - Integration with POS system for hybrid workflows
   """
   
   # Status choices for invoice management
   # 'paid' - Payment has been received in full
   # 'unpaid' - Payment is pending or deferred
   # 'overdue' - Payment is past the due date
   STATUS_CHOICES = [
       ('paid', 'Paid'),
       ('unpaid', 'Unpaid'),
       ('overdue', 'Overdue'),
   ]

   # Unique identifier for the invoice in INV-XXX format
   # May also be POS-XXX for invoices generated from POS transactions
   invoice_number = models.CharField(max_length=20, unique=True)  # INV-001 format
   
   # Reference to the customer account
   # PROTECT prevents deletion of customers with active invoices
   customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
   
   # Transaction date and payment due date
   # Due date can be blank/NULL for immediate payment invoices
   date = models.DateField(default=timezone.now)
   due_date = models.DateField(blank=True, null=True)
   
   # Total amount of the invoice
   # Calculated from sum of invoice items
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   
   # Current status of the invoice
   # Controls payment tracking and overdue notifications
   status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
   
   # Audit fields for tracking creation and modification times
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   def __str__(self):
       """
       String representation of the invoice
       
       Returns the invoice number for easy identification in admin
       interface and debugging output.
       """
       return self.invoice_number

   def is_pos_generated(self):
       """
       Check if this invoice was generated from a POS transaction
       
       Invoices can be generated automatically from paid POS transactions
       to maintain accounting records. This method identifies such invoices.
       
       Returns:
           bool: True if invoice number starts with 'POS-', False otherwise
       """
       return self.invoice_number.startswith('POS-')
   
   def get_pos_reference(self):
       """
       Get the POS reference if this invoice was generated from POS
       
       For invoices generated from POS transactions, this method returns
       the POS number that can be used to reference the original transaction.
       
       Returns:
           str or None: POS number if this is a POS-generated invoice, None otherwise
       """
       if self.is_pos_generated():
           return self.invoice_number
       return None

   class Meta:
       # Default ordering by date, most recent first
       ordering = ['-date']

class InvoiceItem(models.Model):
   """
   Individual Item in an Invoice
   
   Represents a single product or service listed in an invoice. Each invoice
   can have multiple items, and this model tracks the specific details of
   each item including quantity, price, and total amount.
   
   Relationship:
   - Belongs to one Invoice (ForeignKey)
   - References one Product (ForeignKey)
   """
   
   # Reference to the parent invoice
   # Enables cascading deletion - if invoice is deleted, all items are deleted
   invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
   
   # Reference to the product being invoiced
   # SET_NULL allows keeping invoice records even if product is deleted
   product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
   
   # Quantity of the product invoiced
   # PositiveIntegerField ensures only positive quantities
   quantity = models.PositiveIntegerField()
   
   # Price per unit at the time of invoicing
   # Stored separately from product price to maintain historical accuracy
   unit_price = models.DecimalField(max_digits=10, decimal_places=2)
   
   # Total amount for this line item (quantity * unit_price)
   # Calculated and stored for performance and accuracy
   amount = models.DecimalField(max_digits=10, decimal_places=2)

   def __str__(self):
       """
       String representation of the invoice item
       
       Returns a descriptive string with product name and invoice number for
       easy identification in admin interface and debugging output.
       """
       return f"{self.product.name} - {self.invoice.invoice_number}"

   def save(self, *args, **kwargs):
       """
       Custom save method to calculate total before saving
       
       This method ensures that the total amount for the item is always
       correctly calculated as (quantity * unit_price) before saving.
       
       Args:
           *args: Variable length argument list
           **kwargs: Arbitrary keyword arguments
       """
       # Calculate total amount for this line item before saving
       # This ensures data consistency and prevents calculation errors
       self.amount = self.quantity * self.unit_price
       super().save(*args, **kwargs)