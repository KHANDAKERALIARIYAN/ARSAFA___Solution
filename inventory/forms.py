from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'unit_price', 'buying_price', 'expiry_date', 'input_date', 'barcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'buying_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'input_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scan or enter barcode'}),
        } 