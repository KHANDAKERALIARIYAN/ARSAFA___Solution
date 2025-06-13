from django.db import models

# Create your models here.

class Product(models.Model):
    STATUS_CHOICES = [
        ('low', 'Low'),
        ('fair', 'Fair'),
        ('good', 'Good'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    input_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='good')

    def __str__(self):
        return f"{self.name} ({self.category})"
