from django.db import models
from customers.models import Customer

class Lending(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('repaid', 'Repaid'),
        ('overdue', 'Overdue'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='lendings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Percent per year')
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    email_sent_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.customer.name} - {self.amount} ({self.status})" 