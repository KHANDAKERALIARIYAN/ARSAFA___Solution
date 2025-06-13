from django.db import models
from inventory.models import Product

# Create your models here.

class Sale(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.timestamp.date()}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
