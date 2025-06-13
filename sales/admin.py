from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'timestamp', 'total')
    inlines = [SaleItemInline]
    search_fields = ('invoice_id',)
    date_hierarchy = 'timestamp'

admin.site.register(SaleItem)
