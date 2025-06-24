# type: ignore[import-unresolved]
from django.db import models
from django.utils import timezone
from inventory.models import Product
from customers.models import Customer

class Sale(models.Model):
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Sale on {self.date.strftime('%Y-%m-%d')}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} of {self.product.name}" 