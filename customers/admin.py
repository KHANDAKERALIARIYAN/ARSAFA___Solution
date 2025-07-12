from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'outstanding_balance', 'total_purchases', 'last_purchase')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
