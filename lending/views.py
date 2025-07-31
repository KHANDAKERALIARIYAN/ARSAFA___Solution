from django.shortcuts import render, get_object_or_404, redirect
from .models import Lending
from .forms import LendingForm
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from invoices.models import POS
from sales.models import Sale
from django.core.mail import send_mail
from django.conf import settings

@login_required
def lending_dashboard(request):
    total_lendings = Lending.objects.count()
    active_lendings = Lending.objects.filter(status='active').count()
    total_amount = Lending.objects.aggregate(total=Sum('amount'))['total'] or 0
    outstanding = Lending.objects.filter(status__in=['active', 'overdue']).aggregate(total=Sum('amount'))['total'] or 0
    lendings = Lending.objects.select_related('customer').all().order_by('-start_date')
    context = {
        'total_lendings': total_lendings,
        'active_lendings': active_lendings,
        'total_amount': total_amount,
        'outstanding': outstanding,
        'lendings': lendings,
    }
    return render(request, 'lending/lending_dashboard.html', context)

@login_required
def lending_create(request):
    if request.method == 'POST':
        form = LendingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lending_dashboard')
    else:
        form = LendingForm()
    return render(request, 'lending/lending_form.html', {'form': form})

@login_required
def lending_update(request, pk):
    lending = get_object_or_404(Lending, pk=pk)
    if request.method == 'POST':
        form = LendingForm(request.POST, instance=lending)
        if form.is_valid():
            form.save()
            return redirect('lending_dashboard')
    else:
        form = LendingForm(instance=lending)
    return render(request, 'lending/lending_form.html', {'form': form})

@login_required
def lending_delete(request, pk):
    lending = get_object_or_404(Lending, pk=pk)
    
    if request.method == 'POST':
        customer = lending.customer
        customer_name = customer.name
        customer_phone = customer.phone
        
        try:
            # Find related POS bills for this customer
            related_pos_bills = POS.objects.filter(
                customer_name=customer_name,
                contact_number=customer_phone
            )
            
            # Find related sales for this customer
            related_sales = Sale.objects.filter(customer=customer)
            
            # Count items to be deleted
            pos_count = related_pos_bills.count()
            sales_count = related_sales.count()
            
            # Delete related sales first (they reference POS)
            for sale in related_sales:
                sale.delete()
            
            # Delete related POS bills
            for pos_bill in related_pos_bills:
                pos_bill.delete()
            
            # Finally delete the lending record
            lending.delete()
            
            # Show success message with details
            message_parts = [f'Lending record for "{customer_name}" has been deleted successfully.']
            if pos_count > 0:
                message_parts.append(f'{pos_count} POS bill(s) deleted.')
            if sales_count > 0:
                message_parts.append(f'{sales_count} sale record(s) deleted.')
            
            messages.success(request, ' '.join(message_parts))
            
        except Exception as e:
            messages.error(request, f'Error deleting lending record: {str(e)}')
        
        return redirect('lending_dashboard')
    
    # For GET request, show confirmation with related data info
    customer = lending.customer
    related_pos_bills = POS.objects.filter(
        customer_name=customer.name,
        contact_number=customer.phone
    )
    related_sales = Sale.objects.filter(customer=customer)
    
    context = {
        'lending': lending,
        'related_pos_bills': related_pos_bills,
        'related_sales': related_sales,
    }
    return render(request, 'lending/lending_confirm_delete.html', context) 

@login_required
def send_lending_email(request, pk):
    lending = get_object_or_404(Lending, pk=pk)
    customer = lending.customer
    if not customer.email:
        messages.error(request, 'No email address found for this lender.')
        return redirect('lending_dashboard')
    subject = f'Repayment Reminder: Lending Amount Due'
    message = f'Dear {customer.name},\n\nThis is a reminder that you have an outstanding lending amount of ৳{lending.amount} due on {lending.due_date}. Please pay back as soon as possible.\n\nThank you.\nARSAFA SOLUTION'
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
            [customer.email],
            fail_silently=False,
        )
        messages.success(request, f'Email sent to {customer.email}')
    except Exception as e:
        messages.error(request, f'Failed to send email: {e}')
    return redirect('lending_dashboard') 