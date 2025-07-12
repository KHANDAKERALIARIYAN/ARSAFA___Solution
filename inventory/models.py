from django.db import models

# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        # Food & Beverages
        ('produce', 'Produce (Fruits and Vegetables)'),
        ('meat_seafood', 'Meat & Seafood'),
        ('dairy_eggs', 'Dairy & Eggs'),
        ('bakery', 'Bakery'),
        ('frozen_foods', 'Frozen Foods'),
        ('pantry_dry_goods', 'Pantry/Dry Goods'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('canned_goods', 'Canned Goods'),
        ('deli_prepared', 'Deli & Prepared Foods'),
        ('international_specialty', 'International/Specialty Foods'),
        ('condiments_sauces', 'Condiments & Sauces'),
        ('spices_seasonings', 'Spices & Seasonings'),
        ('grains_cereals', 'Grains & Cereals'),
        ('nuts_seeds', 'Nuts & Seeds'),
        
        # Household & Personal Care
        ('household_cleaning', 'Household & Cleaning Supplies'),
        ('health_beauty', 'Health & Beauty'),
        ('baby_care', 'Baby Care'),
        ('personal_care', 'Personal Care & Hygiene'),
        ('laundry_detergents', 'Laundry & Detergents'),
        ('paper_products', 'Paper Products'),
        ('kitchen_utensils', 'Kitchen Utensils'),
        ('home_decor', 'Home Decor & Accessories'),
        
        # Electronics & Technology
        ('electronics', 'Electronics & Gadgets'),
        ('computers_laptops', 'Computers & Laptops'),
        ('mobile_phones', 'Mobile Phones & Accessories'),
        ('audio_video', 'Audio & Video Equipment'),
        ('gaming', 'Gaming & Entertainment'),
        ('cables_adapters', 'Cables & Adapters'),
        ('power_supplies', 'Power Supplies & Batteries'),
        
        # Clothing & Fashion
        ('clothing', 'Clothing & Apparel'),
        ('footwear', 'Footwear & Shoes'),
        ('accessories', 'Fashion Accessories'),
        ('jewelry_watches', 'Jewelry & Watches'),
        ('bags_luggage', 'Bags & Luggage'),
        ('sports_wear', 'Sports & Athletic Wear'),
        
        # Automotive & Tools
        ('automotive', 'Automotive Parts & Accessories'),
        ('tools_hardware', 'Tools & Hardware'),
        ('garden_outdoor', 'Garden & Outdoor'),
        ('construction', 'Construction Materials'),
        ('electrical_supplies', 'Electrical Supplies'),
        ('plumbing', 'Plumbing Supplies'),
        
        # Office & Business
        ('office_supplies', 'Office Supplies'),
        ('stationery', 'Stationery & Paper'),
        ('furniture', 'Furniture & Office Equipment'),
        ('printers_ink', 'Printers & Ink Cartridges'),
        ('business_software', 'Business Software & Licenses'),
        
        # Health & Medical
        ('medical_supplies', 'Medical Supplies'),
        ('pharmaceuticals', 'Pharmaceuticals'),
        ('vitamins_supplements', 'Vitamins & Supplements'),
        ('first_aid', 'First Aid & Safety'),
        ('medical_equipment', 'Medical Equipment'),
        
        # Pet & Animal Care
        ('pet_supplies', 'Pet Supplies'),
        ('pet_food', 'Pet Food & Treats'),
        ('veterinary', 'Veterinary Supplies'),
        ('livestock', 'Livestock & Farm Supplies'),
        
        # Sports & Recreation
        ('sports_equipment', 'Sports Equipment'),
        ('fitness', 'Fitness & Exercise'),
        ('outdoor_recreation', 'Outdoor Recreation'),
        ('toys_games', 'Toys & Games'),
        ('hobbies_crafts', 'Hobbies & Crafts'),
        
        # Books & Media
        ('books', 'Books & Publications'),
        ('magazines', 'Magazines & Newspapers'),
        ('music_movies', 'Music & Movies'),
        ('educational', 'Educational Materials'),
        
        # Miscellaneous
        ('gifts', 'Gifts & Gift Cards'),
        ('seasonal', 'Seasonal Items'),
        ('promotional', 'Promotional Items'),
        ('raw_materials', 'Raw Materials'),
        ('finished_goods', 'Finished Goods'),
        ('other', 'Other'),
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
    barcode = models.CharField(max_length=50, blank=True, null=True, help_text="Product barcode for scanning")
    batch_number = models.CharField(max_length=50, blank=True, null=True, help_text="Batch or lot number for tracking")
    tag_name = models.CharField(max_length=100, blank=True, null=True, help_text="Custom tag or label for the product")

    def save(self, *args, **kwargs):
        # Automatically set status based on quantity
        if self.quantity < 50:
            self.status = 'low'
        else:
            self.status = 'fair'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
