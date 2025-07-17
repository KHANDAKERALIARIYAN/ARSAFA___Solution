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
from customers.models import Customer
from employees.models import Employee

# Create your views here.

@user_passes_test(lambda u: u.is_superuser)
def delete_all_data(request):
    if request.method == 'POST':
        try:
            # Disable signals temporarily to prevent automatic recreation
            from django.db.models.signals import post_save
            from invoices.models import POS
            from invoices.signals import update_modules_on_pos_save
            
            # Disconnect the signal
            post_save.disconnect(update_modules_on_pos_save, sender=POS)
            
            try:
                # Delete in order to respect foreign key constraints
                # 1. Delete all related items first
                SaleItem.objects.all().delete()
                POSItem.objects.all().delete()
                InvoiceItem.objects.all().delete()
                
                # 2. Delete main records
                Sale.objects.all().delete()
                POS.objects.all().delete()
                Invoice.objects.all().delete()
                Lending.objects.all().delete()
                Product.objects.all().delete()
                Customer.objects.all().delete()
                Employee.objects.all().delete()
                
                messages.success(request, '✅ All data has been completely deleted! Your ARSAFA application is now fresh and ready for new data.')
                
            finally:
                # Reconnect the signal
                post_save.connect(update_modules_on_pos_save, sender=POS)
            
        except Exception as e:
            messages.error(request, f'❌ Error deleting data: {str(e)}')
            
    return redirect('admin_dashboard')

def admin_dashboard(request):
    # Get today's date
    today = timezone.now().date()
    
    # Calculate daily sales (only from POS models - including unpaid amounts)
    # Include both paid and unpaid POS amounts in daily sales
    daily_sales_pos_paid = POS.objects.filter(
        date__date=today,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    daily_sales_pos_unpaid = POS.objects.filter(
        date__date=today,
        status='unpaid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Total daily sales (only from POS transactions)
    total_daily_sales = daily_sales_pos_paid + daily_sales_pos_unpaid
    
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
    

    
    # Prepare summary data
    summary = {
        'total_sales_today': total_daily_sales,
        'low_stock_items': low_stock_items,
        'pending_invoices': pending_invoices,
        'credit_balance': credit_balance,
        'low_stock_products': low_stock_products,
        'daily_sales_breakdown': {
            'pos_paid': daily_sales_pos_paid,
            'pos_unpaid': daily_sales_pos_unpaid,
        }
    }
    
    return render(request, 'accounts/admin_dashboard.html', {'summary': summary})
