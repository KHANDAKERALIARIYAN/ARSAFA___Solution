from django.db import models

# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('produce', 'Produce (Fruits and Vegetables)'),
        ('meat_seafood', 'Meat & Seafood'),
        ('dairy_eggs', 'Dairy & Eggs'),
        ('bakery', 'Bakery'),
        ('frozen_foods', 'Frozen Foods'),
        ('pantry_dry_goods', 'Pantry/Dry Goods'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('canned_goods', 'Canned Goods'),
        ('household_cleaning', 'Household & Cleaning Supplies'),
        ('health_beauty', 'Health & Beauty'),
        ('baby_care', 'Baby Care'),
        ('pet_supplies', 'Pet Supplies'),
        ('deli_prepared', 'Deli & Prepared Foods'),
        ('international_specialty', 'International/Specialty Foods'),
    ]
    
    STATUS_CHOICES = [
        ('low', 'Low'),
        ('fair', 'Fair'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    input_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='good')
    barcode = models.CharField(max_length=64, unique=True, blank=True, null=True)
    tag = models.CharField(max_length=50, blank=True, null=True)
    batch = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically set status based on quantity
        if self.quantity < 50:
            self.status = 'low'
        else:
            self.status = 'fair'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
