from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Product
from decimal import Decimal
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Add 100 random products to the inventory'

    def handle(self, *args, **options):
        # Product data for different categories
        products_data = {
            'produce': [
                ('Fresh Tomatoes', 80, 120),
                ('Organic Carrots', 60, 90),
                ('Green Bell Peppers', 100, 150),
                ('Fresh Spinach', 40, 70),
                ('Red Onions', 50, 80),
                ('Cucumbers', 70, 110),
                ('Fresh Garlic', 120, 180),
                ('Green Beans', 90, 140),
                ('Fresh Mushrooms', 150, 220),
                ('Sweet Corn', 80, 120),
                ('Fresh Ginger', 200, 300),
                ('Fresh Turmeric', 180, 280),
                ('Fresh Coriander', 30, 50),
                ('Fresh Mint', 40, 60),
                ('Fresh Basil', 50, 80),
            ],
            'meat_seafood': [
                ('Fresh Chicken Breast', 350, 450),
                ('Beef Mince', 500, 650),
                ('Fresh Fish Fillet', 400, 550),
                ('Pork Chops', 450, 600),
                ('Fresh Shrimp', 800, 1200),
                ('Lamb Chops', 600, 800),
                ('Fresh Salmon', 1200, 1600),
                ('Turkey Breast', 400, 550),
                ('Fresh Tuna', 900, 1200),
                ('Duck Meat', 700, 900),
                ('Fresh Crab', 1000, 1400),
                ('Fresh Mussels', 300, 450),
                ('Fresh Oysters', 500, 700),
                ('Fresh Lobster', 2000, 2800),
                ('Fresh Squid', 400, 600),
            ],
            'dairy_eggs': [
                ('Fresh Milk 1L', 120, 150),
                ('Free Range Eggs (12)', 180, 220),
                ('Natural Yogurt', 100, 140),
                ('Cheddar Cheese', 400, 550),
                ('Butter 250g', 200, 280),
                ('Cream Cheese', 250, 350),
                ('Fresh Cream', 150, 200),
                ('Mozzarella Cheese', 350, 480),
                ('Cottage Cheese', 180, 250),
                ('Sour Cream', 120, 180),
                ('Greek Yogurt', 150, 200),
                ('Fresh Curd', 80, 120),
                ('Paneer', 300, 400),
                ('Fresh Ghee', 800, 1200),
                ('Condensed Milk', 120, 180),
            ],
            'bakery': [
                ('Whole Wheat Bread', 60, 90),
                ('White Bread', 50, 80),
                ('Croissants', 80, 120),
                ('Chocolate Cake', 400, 600),
                ('Fresh Cookies', 120, 180),
                ('Muffins', 100, 150),
                ('Donuts', 80, 120),
                ('Fresh Buns', 40, 60),
                ('Pizza Base', 80, 120),
                ('Fresh Pastries', 150, 220),
                ('Sandwich Bread', 70, 100),
                ('Fresh Rolls', 30, 50),
                ('Cupcakes', 120, 180),
                ('Fresh Bagels', 100, 150),
                ('Fresh Pies', 200, 300),
            ],
            'frozen_foods': [
                ('Frozen Peas', 80, 120),
                ('Frozen Corn', 70, 110),
                ('Frozen Fish Fingers', 200, 300),
                ('Frozen Pizza', 300, 450),
                ('Ice Cream Vanilla', 250, 350),
                ('Frozen French Fries', 120, 180),
                ('Frozen Chicken Nuggets', 180, 280),
                ('Frozen Vegetables Mix', 100, 150),
                ('Frozen Shrimp', 400, 600),
                ('Frozen Meatballs', 250, 380),
                ('Frozen Dumplings', 150, 220),
                ('Frozen Ice Cream Bars', 200, 300),
                ('Frozen Spinach', 60, 100),
                ('Frozen Broccoli', 80, 120),
                ('Frozen Mixed Berries', 150, 220),
            ],
            'pantry_dry_goods': [
                ('Basmati Rice 5kg', 400, 550),
                ('Whole Wheat Flour 2kg', 120, 180),
                ('Sugar 1kg', 80, 120),
                ('Cooking Oil 1L', 150, 200),
                ('Red Lentils 1kg', 120, 180),
                ('Chickpeas 500g', 80, 120),
                ('Black Pepper 100g', 150, 220),
                ('Turmeric Powder 200g', 100, 150),
                ('Cumin Seeds 100g', 120, 180),
                ('Cardamom 50g', 200, 300),
                ('Cinnamon Sticks 100g', 180, 250),
                ('Bay Leaves 50g', 100, 150),
                ('Mustard Seeds 100g', 80, 120),
                ('Fenugreek Seeds 100g', 120, 180),
                ('Coriander Powder 200g', 100, 150),
            ],
            'beverages': [
                ('Mineral Water 1L', 30, 50),
                ('Orange Juice 1L', 120, 180),
                ('Apple Juice 1L', 100, 150),
                ('Green Tea Bags', 150, 220),
                ('Black Tea Bags', 120, 180),
                ('Coffee Beans 250g', 300, 450),
                ('Instant Coffee 200g', 200, 300),
                ('Lemonade 1L', 80, 120),
                ('Coconut Water 500ml', 60, 90),
                ('Energy Drink', 120, 180),
                ('Soda 2L', 80, 120),
                ('Hot Chocolate Mix', 150, 220),
                ('Herbal Tea Bags', 180, 250),
                ('Mango Juice 1L', 100, 150),
                ('Grape Juice 1L', 120, 180),
            ],
            'snacks': [
                ('Potato Chips', 80, 120),
                ('Popcorn', 60, 90),
                ('Mixed Nuts 200g', 200, 300),
                ('Chocolate Bars', 100, 150),
                ('Biscuits', 80, 120),
                ('Crackers', 70, 100),
                ('Dried Fruits Mix', 150, 220),
                ('Peanut Butter 500g', 180, 250),
                ('Granola Bars', 120, 180),
                ('Trail Mix', 200, 300),
                ('Cheese Crackers', 90, 130),
                ('Chocolate Cookies', 100, 150),
                ('Rice Cakes', 80, 120),
                ('Pretzels', 70, 100),
                ('Chocolate Covered Nuts', 250, 350),
            ],
            'canned_goods': [
                ('Canned Tomatoes 400g', 60, 90),
                ('Canned Beans 400g', 80, 120),
                ('Canned Tuna 185g', 120, 180),
                ('Canned Corn 340g', 70, 100),
                ('Canned Mushrooms 400g', 100, 150),
                ('Canned Chickpeas 400g', 80, 120),
                ('Canned Sardines 120g', 150, 220),
                ('Canned Pineapple 567g', 100, 150),
                ('Canned Peaches 411g', 120, 180),
                ('Canned Soup 400g', 80, 120),
                ('Canned Lentils 400g', 70, 100),
                ('Canned Mixed Vegetables', 90, 130),
                ('Canned Fruit Cocktail', 100, 150),
                ('Canned Green Beans', 80, 120),
                ('Canned Carrots', 70, 100),
            ],
            'household_cleaning': [
                ('Dish Soap 500ml', 80, 120),
                ('Laundry Detergent 2L', 200, 300),
                ('All Purpose Cleaner', 120, 180),
                ('Toilet Cleaner', 100, 150),
                ('Glass Cleaner', 80, 120),
                ('Floor Cleaner', 150, 220),
                ('Hand Soap 300ml', 60, 90),
                ('Fabric Softener 1L', 120, 180),
                ('Bleach 1L', 80, 120),
                ('Air Freshener', 100, 150),
                ('Kitchen Towels', 80, 120),
                ('Paper Towels', 60, 90),
                ('Trash Bags', 100, 150),
                ('Sponges Pack', 50, 80),
                ('Scrub Brushes', 60, 90),
            ],
            'health_beauty': [
                ('Shampoo 400ml', 150, 220),
                ('Toothpaste 100g', 80, 120),
                ('Body Wash 400ml', 120, 180),
                ('Face Cream 50g', 200, 300),
                ('Deodorant 150ml', 100, 150),
                ('Hair Conditioner 400ml', 130, 190),
                ('Hand Lotion 200ml', 120, 180),
                ('Sunscreen 100ml', 180, 250),
                ('Lip Balm', 60, 90),
                ('Face Wash 100ml', 150, 220),
                ('Body Lotion 400ml', 180, 250),
                ('Hair Oil 200ml', 120, 180),
                ('Nail Polish', 100, 150),
                ('Perfume 50ml', 500, 800),
                ('Makeup Remover', 120, 180),
            ],
            'baby_care': [
                ('Baby Diapers Size 3', 300, 450),
                ('Baby Wipes 80pcs', 120, 180),
                ('Baby Shampoo 200ml', 150, 220),
                ('Baby Lotion 200ml', 120, 180),
                ('Baby Food 6+ months', 80, 120),
                ('Baby Formula 400g', 400, 600),
                ('Baby Oil 100ml', 100, 150),
                ('Baby Powder 200g', 80, 120),
                ('Baby Soap 100g', 60, 90),
                ('Baby Cream 50g', 100, 150),
                ('Baby Bottles', 200, 300),
                ('Baby Pacifiers', 80, 120),
                ('Baby Bibs Pack', 100, 150),
                ('Baby Socks Pack', 80, 120),
                ('Baby Towels', 150, 220),
            ],
            'pet_supplies': [
                ('Dog Food 2kg', 300, 450),
                ('Cat Food 1.5kg', 250, 380),
                ('Dog Treats 200g', 120, 180),
                ('Cat Treats 100g', 100, 150),
                ('Pet Shampoo 300ml', 150, 220),
                ('Cat Litter 5kg', 200, 300),
                ('Dog Collar', 150, 220),
                ('Cat Collar', 100, 150),
                ('Pet Toys', 80, 120),
                ('Pet Bed Small', 500, 800),
                ('Pet Bowl Set', 120, 180),
                ('Pet Brush', 80, 120),
                ('Pet Leash', 150, 220),
                ('Pet Carrier Small', 800, 1200),
                ('Pet Vitamins', 200, 300),
            ],
            'deli_prepared': [
                ('Fresh Salad Mix', 120, 180),
                ('Hummus 250g', 150, 220),
                ('Fresh Salsa', 100, 150),
                ('Guacamole 200g', 180, 250),
                ('Fresh Pasta', 120, 180),
                ('Fresh Bread Sticks', 80, 120),
                ('Fresh Fruit Salad', 150, 220),
                ('Fresh Vegetable Platter', 200, 300),
                ('Fresh Cheese Platter', 300, 450),
                ('Fresh Meat Platter', 400, 600),
                ('Fresh Sandwich', 120, 180),
                ('Fresh Wraps', 100, 150),
                ('Fresh Sushi Pack', 250, 380),
                ('Fresh Spring Rolls', 150, 220),
                ('Fresh Quiche', 200, 300),
            ],
            'international_specialty': [
                ('Olive Oil Extra Virgin', 400, 600),
                ('Balsamic Vinegar', 300, 450),
                ('Parmesan Cheese', 500, 750),
                ('Prosciutto 100g', 800, 1200),
                ('Truffle Oil 100ml', 1500, 2200),
                ('Saffron 1g', 800, 1200),
                ('Vanilla Extract 100ml', 400, 600),
                ('Maple Syrup 250ml', 300, 450),
                ('Honey 500g', 250, 380),
                ('Dried Herbs Mix', 200, 300),
                ('Exotic Spice Blend', 250, 380),
                ('Gourmet Salt', 150, 220),
                ('Truffle Pasta', 300, 450),
                ('Artisan Bread', 200, 300),
                ('Gourmet Chocolate', 400, 600),
            ]
        }

        categories = list(products_data.keys())
        created_count = 0

        for i in range(100):
            # Select random category
            category = random.choice(categories)
            
            # Select random product from that category
            product_name, min_price, max_price = random.choice(products_data[category])
            
            # Generate random data
            quantity = random.randint(5, 200)
            unit_price = random.randint(min_price, max_price)
            buying_price = unit_price - random.randint(10, 50)
            
            # Generate random dates
            input_date = date.today() - timedelta(days=random.randint(0, 30))
            # For the first 10 products, set expiry within next 7 days
            if i < 10:
                expiry_date = date.today() + timedelta(days=random.randint(0, 7))
            else:
                expiry_date = input_date + timedelta(days=random.randint(30, 365))
            
            # Create product
            product = Product.objects.create(
                name=product_name,
                category=category,
                quantity=quantity,
                unit_price=Decimal(str(unit_price)),
                buying_price=Decimal(str(buying_price)),
                input_date=input_date,
                expiry_date=expiry_date
            )
            
            created_count += 1
            self.stdout.write(f"Created product {created_count}: {product_name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} random products!')
        ) 