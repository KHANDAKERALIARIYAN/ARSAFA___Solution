from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Product
from .forms import ProductForm
from datetime import timedelta
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_query = request.GET.get('category', '')
    sort_query = request.GET.get('sort', '')
    products = Product.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query)
    if category_query:
        products = products.filter(category=category_query)
    # Sorting logic
    if sort_query == 'price_asc':
        products = products.order_by('unit_price')
    elif sort_query == 'price_desc':
        products = products.order_by('-unit_price')
    elif sort_query == 'name_asc':
        products = products.order_by('name')
    elif sort_query == 'name_desc':
        products = products.order_by('-name')
    elif sort_query == 'expiry_asc':
        products = products.order_by('expiry_date')
    elif sort_query == 'expiry_desc':
        products = products.order_by('-expiry_date')
    elif sort_query == 'category_asc':
        products = products.order_by('category')
    low_stock_threshold = 10
    near_expiry_days = 7
    today = timezone.now().date()
    alerts = []
    for product in products:
        if product.quantity <= low_stock_threshold:
            alerts.append(f"Low stock: {product.name} ({product.quantity} left)")
        if product.expiry_date:
            days_to_expiry = (product.expiry_date - today).days
            if 0 <= days_to_expiry <= near_expiry_days:
                alerts.append(f"Near expiry: {product.name} (expires {product.expiry_date})")

    # New inventory management box logic
    low_stock_count = products.filter(quantity__lt=low_stock_threshold).count()
    nearly_expire_count = products.filter(expiry_date__isnull=False, expiry_date__lte=today + timedelta(days=near_expiry_days)).count()
    total_product_count = products.count()
    total_price = sum([(p.quantity or 0) * float(p.unit_price or 0) for p in products])

    categories = Product.CATEGORY_CHOICES

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'alerts': alerts,
        'search_query': search_query,
        'category_query': category_query,
        'sort_query': sort_query,
        'categories': categories,
        'low_stock_count': low_stock_count,
        'nearly_expire_count': nearly_expire_count,
        'total_product_count': total_product_count,
        'total_price': total_price,
    })

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

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/product_detail.html', {'product': product})
