from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Sale, SaleItem
from inventory.models import Product
from django.db import transaction
from django.forms import modelformset_factory
from django import forms
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
try:
    from customers.models import Customer
except ImportError:
    Customer = None

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']

@login_required
def sales_list(request):
    sales = Sale.objects.all().order_by('-timestamp')
    return render(request, 'sales/sales_list.html', {'sales': sales})

@login_required
def sales_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/sales_detail.html', {'sale': sale})

@login_required
def sales_create(request):
    SaleItemFormSet = modelformset_factory(SaleItem, form=SaleItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        formset = SaleItemFormSet(request.POST, queryset=SaleItem.objects.none())
        if formset.is_valid():
            with transaction.atomic():
                sale = Sale.objects.create(total=0, invoice_id=f"INV{Sale.objects.count()+1:05d}")
                total = 0
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.sale = sale
                        item.subtotal = item.quantity * item.unit_price
                        item.save()
                        total += item.subtotal
                        # Optionally update product stock here
                sale.total = total
                sale.save()
                return redirect('sales_detail', pk=sale.pk)
    else:
        formset = SaleItemFormSet(queryset=SaleItem.objects.none())
    return render(request, 'sales/sales_form.html', {'formset': formset})

@login_required
def sales_report(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    year_start = today.replace(month=1, day=1)

    # Total sales and orders
    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0
    total_orders = Sale.objects.count()
    avg_order_value = total_sales / total_orders if total_orders else 0

    # New customers (this week)
    new_customers = 0
    if Customer:
        try:
            new_customers = Customer.objects.filter(created_at__gte=week_start).count()
        except Exception:
            new_customers = 0

    # Daily sales (current week)
    daily_sales = [0]*7
    for i in range(7):
        day = week_start + timedelta(days=i)
        sales = Sale.objects.filter(timestamp__date=day).aggregate(total=Sum('total'))['total'] or 0
        daily_sales[i] = float(sales)

    # Monthly revenue (current year)
    monthly_revenue = [0]*12
    for m in range(1, 13):
        sales = Sale.objects.filter(timestamp__year=today.year, timestamp__month=m).aggregate(total=Sum('total'))['total'] or 0
        monthly_revenue[m-1] = float(sales)

    # Top selling products
    top_products = (
        SaleItem.objects.values('product__name')
        .annotate(units_sold=Sum('quantity'), revenue=Sum('subtotal'))
        .order_by('-units_sold')[:3]
    )
    # Add dummy growth data
    for i, prod in enumerate(top_products):
        prod['growth'] = [12.5, 8.3, -2.1][i] if i < 3 else 0

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'new_customers': new_customers,
        'daily_sales': daily_sales,
        'monthly_revenue': monthly_revenue,
        'top_products': top_products,
        'weekdays': ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        'months': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    }
    return render(request, 'sales/sales_report.html', context)
