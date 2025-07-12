from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from sales.models import Sale, SaleItem
from invoices.models import POS, POSItem, Invoice, InvoiceItem
from lending.models import Lending
from inventory.models import Product

# Create your views here.

@user_passes_test(lambda u: u.is_superuser)
def delete_all_data(request):
    if request.method == 'POST':
        # Delete in order to respect foreign key constraints
        SaleItem.objects.all().delete()
        Sale.objects.all().delete()
        POSItem.objects.all().delete()
        POS.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Lending.objects.all().delete()
        Product.objects.all().delete()
        messages.success(request, 'All sales, POS, invoices, lending records, and inventory have been deleted!')
    return redirect('admin_dashboard')

def admin_dashboard(request):
    # Get today's date
    today = timezone.now().date()
    
    # Calculate daily sales (from both Sale and POS models - including unpaid amounts)
    daily_sales_sale = Sale.objects.filter(
        date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Include both paid and unpaid POS amounts in daily sales
    daily_sales_pos_paid = POS.objects.filter(
        date__date=today,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    daily_sales_pos_unpaid = POS.objects.filter(
        date__date=today,
        status='unpaid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Total daily sales including unpaid amounts
    total_daily_sales = daily_sales_sale + daily_sales_pos_paid + daily_sales_pos_unpaid
    
    # Count low stock items (quantity < 50)
    low_stock_items = Product.objects.filter(quantity__lt=50).count()
    
    # Get low stock products for alerts
    low_stock_products = Product.objects.filter(quantity__lt=50).order_by('quantity')[:5]
    
    # Count pending invoices
    pending_invoices = Invoice.objects.filter(status='unpaid').count()
    
    # Calculate credit balance (sum of unpaid POS transactions)
    credit_balance = POS.objects.filter(status='unpaid').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Get recent activity (last 5 transactions)
    recent_sales = Sale.objects.filter(date__date=today).order_by('-date')[:5]
    recent_pos = POS.objects.filter(date__date=today).order_by('-date')[:5]
    
    # Combine and sort recent activity
    recent_activity = []
    for sale in recent_sales:
        recent_activity.append({
            'type': 'Sale',
            'amount': sale.total_amount,
            'date': sale.date,
            'reference': f"Sale #{sale.id}"
        })
    
    for pos in recent_pos:
        recent_activity.append({
            'type': 'POS',
            'amount': pos.total,
            'date': pos.date,
            'reference': pos.pos_number,
            'status': pos.status
        })
    
    # Sort by date (most recent first)
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:5]
    
    # Prepare summary data
    summary = {
        'total_sales_today': total_daily_sales,
        'low_stock_items': low_stock_items,
        'pending_invoices': pending_invoices,
        'credit_balance': credit_balance,
        'low_stock_products': low_stock_products,
        'recent_activity': recent_activity,
        'daily_sales_breakdown': {
            'sales': daily_sales_sale,
            'pos_paid': daily_sales_pos_paid,
            'pos_unpaid': daily_sales_pos_unpaid,
        }
    }
    
    return render(request, 'accounts/admin_dashboard.html', {'summary': summary})
