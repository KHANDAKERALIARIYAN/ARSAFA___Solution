from django.contrib import admin
from .models import Lending

@admin.register(Lending)
class LendingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'interest_rate', 'start_date', 'due_date', 'status')
    search_fields = ('customer__name',)
    list_filter = ('status',) 