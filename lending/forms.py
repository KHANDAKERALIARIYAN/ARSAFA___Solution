from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Lending

class LendingForm(forms.ModelForm):
    class Meta:
        model = Lending
        fields = '__all__'
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default start date to today and due date to 30 days from today
        if not self.instance.pk:  # Only for new records
            today = timezone.now().date()
            self.fields['start_date'].initial = today
            self.fields['due_date'].initial = today + timedelta(days=30)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        
        if start_date and due_date:
            if due_date <= start_date:
                raise forms.ValidationError("Due date must be after start date.")
        
        return cleaned_data 