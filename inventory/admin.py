from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit_price', 'buying_price', 'expiry_date', 'input_date', 'status')
    search_fields = ('name', 'category')
    list_filter = ('category', 'status')
