from django import forms
from employees.models import Employee

class SalaryCalculationForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    present_days = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    absent_days = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'})) 