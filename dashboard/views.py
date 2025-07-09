from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
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
    return render(request, 'accounts/admin_dashboard.html')
