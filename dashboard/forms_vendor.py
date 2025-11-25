"""
Vendor forms using Django Forms
"""
from django import forms
from .models import Vendor


class VendorForm(forms.ModelForm):
    """
    Form for creating and updating vendors
    """
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'company_name', 'email', 'phone', 'address',
            'city', 'state', 'pincode', 'gst_number',
            'credit_limit', 'outstanding_balance'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vendor name',
                'required': True
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'vendor@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91XXXXXXXXXX',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pincode',
                'required': True
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'GST Number (optional)'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0'
            }),
            'outstanding_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0',
                'readonly': True
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Basic phone validation
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError("Enter a valid phone number")
        return phone
