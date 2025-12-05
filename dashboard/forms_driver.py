""" 
Driver Form for CRUD operations
"""
from django import forms
from .models import Driver


class DriverForm(forms.ModelForm):
    """
    Form for creating and updating drivers - All validations removed
    """
    
    class Meta:
        model = Driver
        fields = [
            'name',
            'phone',
            'license_number',
            'vehicle_number',
            'vehicle_type',
            'vehicle_capacity',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter driver full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter license number'
            }),
            'vehicle_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter vehicle number'
            }),
            'vehicle_type': forms.Select(
                choices=[
                    ('Truck', 'Truck'),
                    ('Mini Truck', 'Mini Truck'),
                    ('Trailer', 'Trailer'),
                    ('Tanker', 'Tanker'),
                ],
                attrs={'class': 'form-input'}
            ),
            'vehicle_capacity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter capacity in bags'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle-checkbox'
            })
        }
        labels = {
            'name': 'Driver Name',
            'phone': 'Phone Number',
            'license_number': 'License Number',
            'vehicle_number': 'Vehicle Number',
            'vehicle_type': 'Vehicle Type',
            'vehicle_capacity': 'Vehicle Capacity',
            'is_active': 'Active Status'
        }