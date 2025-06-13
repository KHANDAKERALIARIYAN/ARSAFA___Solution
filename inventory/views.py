from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Product
from .forms import ProductForm
from datetime import timedelta
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def product_list(request):
    products = Product.objects.all()
    low_stock_threshold = 10
    near_expiry_days = 7
    today = timezone.now().date()
    alerts = []
    for product in products:
        if product.quantity <= low_stock_threshold:
            alerts.append(f"Low stock: {product.name} ({product.quantity} left)")
        if product.expiry_date and (product.expiry_date - today).days <= near_expiry_days:
            alerts.append(f"Near expiry: {product.name} (expires {product.expiry_date})")
    return render(request, 'inventory/product_list.html', {'products': products, 'alerts': alerts})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})
