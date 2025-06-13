from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'date', 'due_date', 'amount', 'status')
    list_filter = ('status', 'date', 'due_date')
    search_fields = ('invoice_number', 'customer__name')
    inlines = [InvoiceItemInline]
    date_hierarchy = 'date' 