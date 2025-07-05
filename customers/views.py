from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from invoices.models import POS

# Create your views here.

@login_required
def customer_dashboard(request):
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(status='active').count()
    total_sales = Customer.objects.aggregate(total=Sum('total_purchases'))['total'] or 0
    outstanding_balance = Customer.objects.aggregate(total=Sum('outstanding_balance'))['total'] or 0
    customers = Customer.objects.all().order_by('-last_purchase')
    # Fetch most recent POS status for each customer
    pos_statuses = {}
    for c in customers:
        pos = POS.objects.filter(customer_name=c.name, contact_number=c.phone).order_by('-date').first()
        pos_statuses[c.pk] = pos
    context = {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'total_sales': total_sales,
        'outstanding_balance': outstanding_balance,
        'customers': customers,
        'pos_statuses': pos_statuses,
    }
    return render(request, 'customers/customers_dashboard.html', context)

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_dashboard')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_dashboard')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})
