from django.db import models

# Create your models here.

class Customer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_purchase = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
