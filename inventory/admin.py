from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit_price', 'buying_price', 'expiry_date', 'input_date', 'status', 'low_stock_threshold')
    search_fields = ('name', 'category')
    list_filter = ('category', 'status')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'barcode')
        }),
        ('Inventory Details', {
            'fields': ('quantity', 'unit_price', 'buying_price', 'low_stock_threshold', 'status')
        }),
        ('Dates & Tracking', {
            'fields': ('expiry_date', 'input_date', 'tag', 'batch')
        }),
    )
