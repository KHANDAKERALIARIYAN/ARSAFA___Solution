from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemForm
from datetime import timedelta

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    
    # Calculate statistics
    total_invoices = invoices.count()
    paid_invoices = invoices.filter(status='paid').count()
    unpaid_invoices = invoices.filter(status='unpaid').count()
    overdue_invoices = invoices.filter(status='overdue').count()
    
    total_amount = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    amount_received = invoices.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'invoices': invoices,
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
                
                messages.success(request, 'Item added successfully.')
                return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('item_id')
            InvoiceItem.objects.filter(id=item_id).delete()
            
            # Update invoice amount
            invoice.amount = invoice.items.aggregate(Sum('amount'))['amount__sum'] or 0
            invoice.save()
            
            messages.success(request, 'Item removed successfully.')
            return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'checkout' in request.POST:
            invoice.status = 'paid'
            invoice.save()
            messages.success(request, 'Checkout complete. Invoice marked as paid.')
            return redirect('invoice_detail', invoice_id=invoice.id)
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Invoice.STATUS_CHOICES):
                invoice.status = new_status
                invoice.save()
                messages.success(request, 'Invoice status updated successfully.')
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