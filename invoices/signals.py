from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import POS, POSItem, Invoice, InvoiceItem
from customers.models import Customer
from lending.models import Lending
from sales.models import Sale, SaleItem
from decimal import Decimal
from django.utils import timezone
import logging
from django.db.models import Sum

logger = logging.getLogger(__name__)

@receiver(post_save, sender=POSItem)
def decrease_stock_on_item_creation(sender, instance, created, **kwargs):
    if created:
        try:
            product = instance.product
            if product and product.quantity >= instance.quantity:
                product.quantity -= instance.quantity
                product.save()
                logger.info(f"Stock decreased for product {product.name}: {instance.quantity} units")
            else:
                logger.warning(f"Insufficient stock for product {product.name if product else 'Unknown'}")
        except Exception as e:
            logger.error(f"Error decreasing stock: {e}")

@receiver(post_delete, sender=POSItem)
def increase_stock_on_item_deletion(sender, instance, **kwargs):
    try:
        product = instance.product
        if product:
            product.quantity += instance.quantity
            product.save()
            logger.info(f"Stock increased for product {product.name}: {instance.quantity} units")
    except Exception as e:
        logger.error(f"Error increasing stock: {e}")

@receiver(post_save, sender=POS)
def update_modules_on_pos_save(sender, instance, created, **kwargs):
    try:
        # 1. Update or create Customer
        customer, created_cust = Customer.objects.get_or_create(
            name=instance.customer_name,
            phone=instance.contact_number,
            defaults={
                'email': instance.email or '',
            }
        )
        # Always update email if changed
        if instance.email and customer.email != instance.email:
            customer.email = instance.email
        
        # Get all POS bills for this customer
        all_pos_bills = POS.objects.filter(
            customer_name=customer.name,
            contact_number=customer.phone
        )
        
        # Calculate totals
        total_purchases = all_pos_bills.aggregate(total=Sum('total'))['total'] or 0
        unpaid_pos_bills = all_pos_bills.filter(status='unpaid')
        outstanding_balance = unpaid_pos_bills.aggregate(total=Sum('total'))['total'] or 0
        
        # Update customer data
        customer.total_purchases = total_purchases
        customer.outstanding_balance = outstanding_balance
        customer.last_purchase = instance.date.date()
        customer.save()
        logger.info(f"Customer {customer.name} updated for POS {instance.pos_number}")

        # 2. Lending Module - Only for unpaid POS transactions
        if customer and instance.status == 'unpaid':
            from datetime import timedelta
            
            # Set start date to today and due date to 30 days from today
            start_date = instance.date.date()
            due_date = start_date + timedelta(days=30)  # 30 days grace period
            
            # Get or create lending record
            lending, l_created = Lending.objects.get_or_create(
                customer=customer,
                status='active',
                defaults={
                    'amount': outstanding_balance,  # Use total unpaid amount
                    'interest_rate': Decimal('0.00'),
                    'start_date': start_date,
                    'due_date': due_date,
                    'notes': f'POS {instance.pos_number} unpaid. Due in 30 days.'
                }
            )
            if not l_created:
                # Update lending amount to total unpaid amount
                lending.amount = outstanding_balance
                lending.save()
            logger.info(f"Lending record {'created' if l_created else 'updated'} for POS {instance.pos_number}")
        
        # 2b. Remove lending record if POS is marked as paid
        elif customer and instance.status == 'paid':
            # Check if there are any unpaid POS bills for this customer
            unpaid_pos_bills = POS.objects.filter(
                customer_name=customer.name,
                contact_number=customer.phone,
                status='unpaid'
            ).exclude(pk=instance.pk)  # Exclude current POS bill
            
            if not unpaid_pos_bills.exists():
                # No unpaid bills left, remove lending record
                lending_records = Lending.objects.filter(customer=customer)
                for lending in lending_records:
                    lending.delete()
                    logger.info(f"Removed lending record for {customer.name} - all bills paid")
            else:
                # Still has unpaid bills, update lending amount
                total_unpaid = unpaid_pos_bills.aggregate(total=Sum('total'))['total'] or 0
                lending_records = Lending.objects.filter(customer=customer)
                for lending in lending_records:
                    lending.amount = total_unpaid
                    lending.save()
                    logger.info(f"Updated lending record for {customer.name} - amount: {total_unpaid}")

        # 3. Sales Module - Only for paid POS transactions
        if instance.status == 'paid':
            customer = Customer.objects.filter(name=instance.customer_name, phone=instance.contact_number).first()
            sale, s_created = Sale.objects.get_or_create(
                date=instance.date,
                customer=customer,
                pos=instance,
                defaults={'total_amount': instance.total}
            )
            
            if not s_created:
                sale.total_amount = instance.total
                sale.save()
            else: # If a new sale is created, populate its items
                for pos_item in instance.items.all():
                    SaleItem.objects.create(
                        sale=sale,
                        product=pos_item.product,
                        quantity=pos_item.quantity,
                        unit_price=pos_item.unit_price
                    )
            logger.info(f"Sale record {'created' if s_created else 'updated'} for POS {instance.pos_number}")

        # 4. Invoices Module
        if customer:
            invoice = Invoice.objects.filter(invoice_number=instance.pos_number).first()
            if invoice:
                invoice.customer = customer
                invoice.amount = instance.total
                invoice.status = instance.status
                invoice.date = instance.date.date()
                invoice.save()
                logger.info(f"Invoice {invoice.invoice_number} updated for POS {instance.pos_number}")
            else:
                invoice = Invoice.objects.create(
                    invoice_number=instance.pos_number,
                    customer=customer,
                    date=instance.date.date(),
                    amount=instance.total,
                    status=instance.status
                )
                logger.info(f"New invoice {invoice.invoice_number} created for POS {instance.pos_number}")
            
            # Sync InvoiceItems with POSItems
            InvoiceItem.objects.filter(invoice=invoice).delete()
            for pos_item in instance.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=pos_item.product,
                    quantity=pos_item.quantity,
                    unit_price=pos_item.unit_price,
                    amount=pos_item.total
                )
            logger.info(f"Invoice items synced for invoice {invoice.invoice_number}")
            
    except Exception as e:
        logger.error(f"Error in update_modules_on_pos_save for POS {instance.pos_number}: {e}")

@receiver(post_delete, sender=POS)
def delete_invoice_customer_lending_on_pos_delete(sender, instance, **kwargs):
    """
    When a POS is deleted, also delete the related Invoice (and its items), Lending records, and the Customer if they have no other activity.
    """
    try:
        from invoices.models import Invoice, InvoiceItem
        invoice = Invoice.objects.filter(invoice_number=instance.pos_number).first()
        if invoice:
            InvoiceItem.objects.filter(invoice=invoice).delete()
            invoice.delete()
            logger.info(f"Deleted invoice {invoice.invoice_number} and its items for POS {instance.pos_number}")

        from lending.models import Lending
        customer = Customer.objects.filter(name=instance.customer_name, phone=instance.contact_number).first()
        if customer:
            lending_records = Lending.objects.filter(customer=customer)
            for lending in lending_records:
                lending.delete()
                logger.info(f"Deleted lending record for customer {customer.name}")

            # Delete Customer if no remaining POS, sales, or lending records
            has_pos = POS.objects.filter(customer_name=customer.name, contact_number=customer.phone).exists()
            from sales.models import Sale
            has_sales = Sale.objects.filter(customer=customer).exists()
            has_lending = Lending.objects.filter(customer=customer).exists()
            if not (has_pos or has_sales or has_lending):
                logger.info(f"Deleting customer {customer.name} as they have no remaining activity.")
                customer.delete()
    except Exception as e:
        logger.error(f"Error deleting related records for POS {instance.pos_number}: {e}") 