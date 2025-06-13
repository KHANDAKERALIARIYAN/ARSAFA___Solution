from django import forms
from .models import Invoice, InvoiceItem
from customers.models import Customer
from inventory.models import Product

class InvoiceForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Invoice
        fields = ['customer', 'date']

class InvoiceItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['unit_price'].initial = kwargs['instance'].product.unit_price 