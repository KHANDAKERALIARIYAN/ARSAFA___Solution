from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'unit_price', 'buying_price', 'selling_price', 'expiry_date', 'input_date', 'status'] 