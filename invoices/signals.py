from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import POS, POSItem, Invoice, InvoiceItem
from customers.models import Customer
from lending.models import Lending
from sales.models import Sale, SaleItem
from decimal import Decimal
from django.utils import timezone

@receiver(post_save, sender=POSItem)
def decrease_stock_on_item_creation(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.quantity -= instance.quantity
        product.save()

@receiver(post_delete, sender=POSItem)
def increase_stock_on_item_deletion(sender, instance, **kwargs):
    product = instance.product
    product.quantity += instance.quantity
    product.save()

@receiver(post_save, sender=POS)
def update_modules_on_pos_save(sender, instance, created, **kwargs):
    # 1. Update or create Customer
    customer, created_cust = Customer.objects.get_or_create(
        name=instance.customer_name,
        phone=instance.contact_number,
        defaults={
            'email': instance.email or '',
            'status': 'active',
        }
    )
    # Always update email if changed
    if instance.email and customer.email != instance.email:
        customer.email = instance.email
    # Update total_purchases and outstanding_balance
    if instance.status == 'paid':
        customer.total_purchases += instance.total
        customer.outstanding_balance = max(Decimal('0.00'), customer.outstanding_balance - instance.total)
    else:
        customer.outstanding_balance += instance.total
    customer.last_purchase = instance.date.date()
    customer.save()

    # 2. Lending Module
    if customer and instance.status == 'unpaid':
        lending, l_created = Lending.objects.get_or_create(
            customer=customer,
            status='active',
            defaults={
                'amount': instance.total,
                'interest_rate': Decimal('0.00'),
                'start_date': instance.date.date(),
                'due_date': instance.date.date(),
                'notes': f'POS {instance.pos_number} unpaid.'
            }
        )
        if not l_created:
            lending.amount += instance.total
            lending.save()

    # 3. Sales Module
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


    # 4. Invoices Module
    if customer:
        invoice = Invoice.objects.filter(invoice_number=instance.pos_number).first()
        if invoice:
            invoice.customer = customer
            invoice.amount = instance.total
            invoice.status = instance.status
            invoice.date = instance.date.date()
            invoice.save()
        else:
            invoice = Invoice.objects.create(
                invoice_number=instance.pos_number,
                customer=customer,
                date=instance.date.date(),
                amount=instance.total,
                status=instance.status
            )
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

@receiver(post_delete, sender=POS)
def delete_sales_on_pos_delete(sender, instance, **kwargs):
    """
    When a POS is deleted, also delete the corresponding Sale, SaleItems, Invoice, and InvoiceItems.
    Now uses the ForeignKey for robust matching.
    """
    # Delete related Sale and SaleItems
    for sale in Sale.objects.filter(pos=instance):
        SaleItem.objects.filter(sale=sale).delete()
        sale.delete()

    # Delete related Invoice and InvoiceItems
    invoice = Invoice.objects.filter(invoice_number=instance.pos_number).first()
    if invoice:
        InvoiceItem.objects.filter(invoice=invoice).delete()
        invoice.delete()

    # 1. Update Customer
    customer = Customer.objects.filter(name=instance.customer_name, phone=instance.contact_number).first()
    if customer:
        # Update total_purchases and outstanding_balance
        if instance.status == 'paid':
            customer.total_purchases += instance.total
            customer.outstanding_balance = max(Decimal('0.00'), customer.outstanding_balance - instance.total)
        else:
            customer.outstanding_balance += instance.total
        customer.last_purchase = instance.date.date()
        customer.save()

    # 2. Lending Module
    if customer and instance.status == 'unpaid':
        lending, l_created = Lending.objects.get_or_create(
            customer=customer,
            status='active',
            defaults={
                'amount': instance.total,
                'interest_rate': Decimal('0.00'),
                'start_date': instance.date.date(),
                'due_date': instance.date.date(),
                'notes': f'POS {instance.pos_number} unpaid.'
            }
        )
        if not l_created:
            lending.amount += instance.total
            lending.save()

    # 3. Sales Module
    if instance.status == 'paid':
        customer = Customer.objects.filter(name=instance.customer_name, phone=instance.contact_number).first()
        sale, s_created = Sale.objects.get_or_create(
            date=instance.date,
            customer=customer,
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


    # 4. Invoices Module
    if customer:
        invoice = Invoice.objects.filter(invoice_number=instance.pos_number).first()
        if invoice:
            invoice.customer = customer
            invoice.amount = instance.total
            invoice.status = instance.status
            invoice.date = instance.date.date()
            invoice.save()
        else:
            invoice = Invoice.objects.create(
                invoice_number=instance.pos_number,
                customer=customer,
                date=instance.date.date(),
                amount=instance.total,
                status=instance.status
            )
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