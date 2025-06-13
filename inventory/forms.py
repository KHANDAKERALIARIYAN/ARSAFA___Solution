from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'unit_price', 'buying_price', 'expiry_date', 'input_date', 'status']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'input_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        } 