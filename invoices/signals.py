from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import POS, POSItem, Invoice, InvoiceItem
from customers.models import Customer
from lending.models import Lending
from sales.models import Sale
from decimal import Decimal
from django.utils import timezone

@receiver(post_save, sender=POS)
def update_modules_on_pos_save(sender, instance, created, **kwargs):
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
    sale, s_created = Sale.objects.get_or_create(
        invoice_id=instance.pos_number,
        defaults={
            'total': instance.total,
            'timestamp': instance.date
        }
    )
    if not s_created:
        sale.total = instance.total
        sale.timestamp = instance.date
        sale.save()

    # 4. Invoices Module
    if customer:
        invoice, i_created = Invoice.objects.get_or_create(
            invoice_number=instance.pos_number,
            defaults={
                'customer': customer,
                'date': instance.date.date(),
                'amount': instance.total,
                'status': instance.status
            }
        )
        if not i_created:
            invoice.amount = instance.total
            invoice.status = instance.status
            invoice.date = instance.date.date()
            invoice.save()
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