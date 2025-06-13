from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=100)
    nid = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()

    def __str__(self):
        return self.name
