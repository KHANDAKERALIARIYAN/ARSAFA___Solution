from django.contrib import admin
from .models import Invoice, InvoiceItem, POS, POSItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class POSItemInline(admin.TabularInline):
    model = POSItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'date', 'due_date', 'amount', 'status')
    list_filter = ('status', 'date', 'due_date')
    search_fields = ('invoice_number', 'customer__name')
    inlines = [InvoiceItemInline]
    date_hierarchy = 'date'

@admin.register(POS)
class POSAdmin(admin.ModelAdmin):
    list_display = ('pos_number', 'customer_name', 'contact_number', 'date', 'total', 'status')
    list_filter = ('status', 'date')
    search_fields = ('pos_number', 'customer_name', 'contact_number')
    inlines = [POSItemInline]
    date_hierarchy = 'date' 