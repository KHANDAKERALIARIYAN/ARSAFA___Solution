from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import Invoice, InvoiceItem, POS, POSItem
from .forms import InvoiceForm, InvoiceItemForm, POSForm, POSItemForm
from datetime import timedelta
from django.urls import reverse
from inventory.models import Product
from customers.models import Customer
from django.views.decorators.http import require_GET
from decimal import Decimal

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    paid_pos_sales = POS.objects.filter(status='paid')

    combined_list = []
    
    # Process standard invoices
    for inv in invoices:
        combined_list.append({
            'id': inv.id,
            'number': inv.invoice_number,
            'customer_name': inv.customer.name,
            'amount': inv.amount,
            'status': inv.status,
            'date': inv.date,
            'due_date': inv.due_date,
            'type': 'invoice'
        })

    # Process paid POS sales
    for pos in paid_pos_sales:
        combined_list.append({
            'id': pos.id,
            'number': pos.pos_number,
            'customer_name': pos.customer_name,
            'amount': pos.total,
            'status': 'paid',  # POS sales in this list are always paid
            'date': pos.date.date(),
            'due_date': pos.date.date(),
            'type': 'pos'
        })
    
    # Sort the combined list by date, most recent first
    combined_list.sort(key=lambda x: x['date'], reverse=True)

    # Calculate statistics from the combined list
    total_invoices = len(combined_list)
    paid_invoices = sum(1 for item in combined_list if item['status'] == 'paid')
    unpaid_invoices = sum(1 for item in combined_list if item['status'] == 'unpaid')
    overdue_invoices = sum(1 for item in combined_list if item['status'] == 'overdue')
    
    total_amount = sum(item['amount'] for item in combined_list)
    amount_received = sum(item['amount'] for item in combined_list if item['status'] == 'paid')
    
    context = {
        'invoices': combined_list,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'overdue_invoices': overdue_invoices,
        'total_amount': total_amount,
        'amount_received': amount_received,
    }
    return render(request, 'invoices/invoice_list.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            # Generate invoice number (INV-001 format)
            last_invoice = Invoice.objects.order_by('-invoice_number').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[1])
                invoice.invoice_number = f'INV-{str(last_number + 1).zfill(3)}'
            else:
                invoice.invoice_number = 'INV-001'
            invoice.save()
            return redirect('invoice_edit', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    
    return render(request, 'invoices/invoice_form.html', {'form': form})

@login_required
def invoice_edit(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    
    if request.method == 'POST':
        if 'add_item' in request.POST:
            item_form = InvoiceItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.invoice = invoice
                item.save()
                
                # Update invoice amount
                invoice.amount = invoice.items.aggregate(Sum('amount'))['amount__sum'] or 0
                invoice.save()
                
                # messages.success(request, 'Item added successfully.')
                return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('item_id')
            InvoiceItem.objects.filter(id=item_id).delete()
            
            # Update invoice amount
            invoice.amount = invoice.items.aggregate(Sum('amount'))['amount__sum'] or 0
            invoice.save()
            
            # messages.success(request, 'Item removed successfully.')
            return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'checkout' in request.POST:
            invoice.status = 'paid'
            invoice.save()
            # messages.success(request, 'Checkout complete. Invoice marked as paid.')
            return redirect('invoice_detail', invoice_id=invoice.id)
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Invoice.STATUS_CHOICES):
                invoice.status = new_status
                invoice.save()
                # messages.success(request, 'Invoice status updated successfully.')
                return redirect('invoice_list')
    
    item_form = InvoiceItemForm()
    context = {
        'invoice': invoice,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'invoices/invoice_edit.html', context)

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

@login_required
def pos_list(request):
    pos_list = POS.objects.all()
    today = timezone.now().date()
    total_pos = pos_list.count()
    paid_pos = pos_list.filter(status='paid').count()
    unpaid_pos = pos_list.filter(status='unpaid').count()
    # Only paid POS for today
    total_revenue = POS.objects.filter(status='paid', date__date=today).aggregate(Sum('total'))['total__sum'] or 0

    context = {
        'pos_list': pos_list,
        'total_pos': total_pos,
        'paid_pos': paid_pos,
        'unpaid_pos': unpaid_pos,
        'total_revenue': total_revenue,
    }
    return render(request, 'invoices/pos_list.html', context)

@login_required
def pos_create(request):
    if request.method == 'POST':
        form = POSForm(request.POST)
        if form.is_valid():
            pos = form.save(commit=False)
            # Generate POS number (POS-001 format)
            last_pos = POS.objects.order_by('-pos_number').first()
            if last_pos:
                last_number = int(last_pos.pos_number.split('-')[1])
                pos.pos_number = f'POS-{str(last_number + 1).zfill(3)}'
            else:
                pos.pos_number = 'POS-001'
            pos.save()
            return redirect('pos_edit', pos_id=pos.id)
    else:
        form = POSForm()
    
    return render(request, 'invoices/pos_form.html', {'form': form})

@login_required
def pos_edit(request, pos_id):
    pos = get_object_or_404(POS, id=pos_id)
    items = pos.items.all()
    
    if request.method == 'POST':
        if 'add_item' in request.POST:
            item_form = POSItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.pos = pos
                item.save()
                
                # Update POS subtotal
                pos.subtotal = pos.items.aggregate(Sum('total'))['total__sum'] or 0
                pos.save()
                
                # messages.success(request, 'Item added successfully.')
                return redirect('pos_edit', pos_id=pos.id)
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('item_id')
            POSItem.objects.filter(id=item_id).delete()
            
            # Update POS subtotal
            pos.subtotal = pos.items.aggregate(Sum('total'))['total__sum'] or 0
            pos.save()
            
            # messages.success(request, 'Item removed successfully.')
            return redirect('pos_edit', pos_id=pos.id)
        elif 'update_discount' in request.POST:
            discount = request.POST.get('discount', 0)
            try:
                discount = Decimal(discount)
                if discount < 0:
                    raise ValueError('Discount cannot be negative')
                if discount > pos.subtotal:
                    # messages.error(request, 'Discount cannot exceed subtotal.')
                    pass
                else:
                    pos.discount = discount
                    pos.save()
                    # messages.success(request, 'Discount updated successfully.')
            except (ValueError, InvalidOperation):
                # messages.error(request, 'Invalid discount amount.')
                pass
            return redirect('pos_edit', pos_id=pos.id)
        elif 'make_payment' in request.POST:
            pos.status = 'paid'
            pos.save()
            # messages.success(request, 'Payment completed successfully.')
            return redirect('pos_detail', pos_id=pos.id)
    
    item_form = POSItemForm()
    context = {
        'pos': pos,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'invoices/pos_edit.html', context)

@login_required
def pos_detail(request, pos_id):
    pos = get_object_or_404(POS, id=pos_id)
    if request.method == 'POST':
        if 'update_discount' in request.POST:
            discount = request.POST.get('discount', 0)
            try:
                discount = Decimal(discount)
                if discount < 0:
                    raise ValueError('Discount cannot be negative')
                if discount > pos.subtotal:
                    # messages.error(request, 'Discount cannot exceed subtotal.')
                    pass
                else:
                    pos.discount = discount
                    pos.save()
                    # messages.success(request, 'Discount updated successfully.')
            except (ValueError, InvalidOperation):
                # messages.error(request, 'Invalid discount amount.')
                pass
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(POS.STATUS_CHOICES):
                pos.status = new_status
                pos.save()
                # messages.success(request, f'Payment status updated to {new_status.title()}.')
        return redirect('pos_detail', pos_id=pos.id)
    return render(request, 'invoices/pos_detail.html', {'pos': pos})

@login_required
def pos_delete(request, pos_id):
    pos = get_object_or_404(POS, id=pos_id)
    if request.method == 'POST':
        pos.delete()
        # messages.success(request, 'POS transaction deleted successfully.')
        return redirect('pos_list')
    return redirect('pos_list')

@require_GET
def get_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Use unit_price if selling_price is None, otherwise use selling_price
    price = product.unit_price
    return JsonResponse({'price': price}) 