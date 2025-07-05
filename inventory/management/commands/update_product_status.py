from django.core.management.base import BaseCommand
from inventory.models import Product

class Command(BaseCommand):
    help = 'Update all product statuses according to the new rules (fair > 50, low <= 50)'

    def handle(self, *args, **options):
        updated = 0
        for product in Product.objects.all():
            old_status = product.status
            if product.quantity <= 50:
                product.status = 'low'
            else:
                product.status = 'fair'
            if product.status != old_status:
                product.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} products to match new status rules.')) 