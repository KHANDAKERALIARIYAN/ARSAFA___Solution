from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncDay
from .models import Sale, SaleItem
from customers.models import Customer
from inventory.models import Product
from datetime import timedelta, datetime
from django.utils import timezone
import json
from invoices.models import POS

def sales_report(request):
    period = request.GET.get('period', '30')
    days = int(period)

    # --- Date Ranges ---
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    prev_end_date = start_date
    prev_start_date = prev_end_date - timedelta(days=days)

    # --- Summary Cards ---
    sales = Sale.objects.filter(date__range=[start_date, end_date])
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales.count()
    avg_order_value = sales.aggregate(avg=Avg('total_amount'))['avg'] or 0
    paid_pos_total = POS.objects.filter(status='paid', date__range=[start_date, end_date]).aggregate(total=Sum('total'))['total'] or 0
    new_customers = Customer.objects.filter(created_at__range=[start_date, end_date]).count()
    unpaid_pos_total = POS.objects.filter(status='unpaid', date__range=[start_date, end_date]).aggregate(total=Sum('total'))['total'] or 0

    # --- Daily Sales Chart (Whole Week - Last 7 Days) ---
    # Get the start of the current week (Monday)
    today = timezone.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    
    # Generate all 7 days of the week
    week_days = []
    daily_sales_data = []
    
    for i in range(7):
        current_day = week_start + timedelta(days=i)
        week_days.append(current_day)
        
        # Get sales for this specific day
        day_sales = Sale.objects.filter(
            date__date=current_day
        ).aggregate(total=Sum('total_amount'))
        
        daily_sales_data.append({
            'day': current_day,
            'total': day_sales['total'] or 0
        })
    
    daily_labels = [day.strftime('%a') for day in week_days]
    daily_totals = [float(data['total']) for data in daily_sales_data]

    # --- Top Selling Products Chart ---
    top_products_current = SaleItem.objects.filter(sale__date__range=[start_date, end_date]) \
        .values('product__name', 'product__id') \
        .annotate(
            units_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-units_sold')[:10]  # Get top 10 for better chart visualization

    top_products_data = []
    product_names = []
    product_units = []
    product_revenues = []
    
    for p in top_products_current:
        prev_sales = SaleItem.objects.filter(
            sale__date__range=[prev_start_date, prev_end_date],
            product__id=p['product__id']
        ).aggregate(prev_units=Sum('quantity'))
        
        prev_units_sold = prev_sales['prev_units'] or 0
        
        growth = 0
        if prev_units_sold > 0:
            growth = ((p['units_sold'] - prev_units_sold) / prev_units_sold) * 100
        elif p['units_sold'] > 0:
            growth = 100 # Infinite growth becomes 100%

        top_products_data.append({
            'product__name': p['product__name'],
            'units_sold': p['units_sold'],
            'revenue': p['revenue'],
            'growth': growth,
        })
        
        # Data for the chart
        product_names.append(p['product__name'])
        product_units.append(p['units_sold'])
        product_revenues.append(float(p['revenue']))
        
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'paid_pos_total': paid_pos_total,
        'unpaid_pos_total': unpaid_pos_total,
        'daily_labels': json.dumps(daily_labels),
        'daily_totals': json.dumps(daily_totals),
        'top_products': top_products_data,
        'product_names': json.dumps(product_names),
        'product_units': json.dumps(product_units),
        'product_revenues': json.dumps(product_revenues),
        'section': 'sales_report',
        'selected_period': period,
    }
    return render(request, 'sales/sales_report.html', context) 