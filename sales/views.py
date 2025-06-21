from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncDay
from .models import Sale, SaleItem
from customers.models import Customer
from inventory.models import Product
from datetime import timedelta
from django.utils import timezone
import json

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
    new_customers = Customer.objects.filter(created_at__range=[start_date, end_date]).count()

    # --- Daily Sales Chart (Last 7 Days) ---
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    daily_sales_data = Sale.objects.filter(date__date__gt=seven_days_ago) \
        .annotate(day=TruncDay('date')) \
        .values('day') \
        .annotate(total=Sum('total_amount')) \
        .order_by('day')
    
    daily_labels = [s['day'].strftime('%a') for s in daily_sales_data]
    daily_totals = [float(s['total']) for s in daily_sales_data]

    # --- Monthly Revenue Trend (Last 6 Months) ---
    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly_revenue_data = Sale.objects.filter(date__date__gt=six_months_ago) \
        .annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(total=Sum('total_amount')) \
        .order_by('month')
        
    monthly_labels = [r['month'].strftime('%b') for r in monthly_revenue_data]
    monthly_totals = [float(r['total']) for r in monthly_revenue_data]

    # --- Top Selling Products with Growth ---
    top_products_current = SaleItem.objects.filter(sale__date__range=[start_date, end_date]) \
        .values('product__name', 'product__id') \
        .annotate(
            units_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-units_sold')[:5]

    top_products_data = []
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
        
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'new_customers': new_customers,
        'daily_labels': json.dumps(daily_labels),
        'daily_totals': json.dumps(daily_totals),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_totals': json.dumps(monthly_totals),
        'top_products': top_products_data,
        'section': 'sales_report',
        'selected_period': period,
    }
    return render(request, 'sales/sales_report.html', context) 