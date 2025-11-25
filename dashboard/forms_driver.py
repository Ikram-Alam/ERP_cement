"""
Driver Form for CRUD operations
"""
from django import forms
from .models import Driver


class DriverForm(forms.ModelForm):
    """
    Form for creating and updating drivers
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
                'class': 'form-control',
                'placeholder': 'Enter driver full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91XXXXXXXXXX'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DL-XXXXXXXXX'
            }),
            'vehicle_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX-00-XX-0000'
            }),
            'vehicle_type': forms.Select(
                choices=[
                    ('Truck', 'Truck'),
                    ('Mini Truck', 'Mini Truck'),
                    ('Trailer', 'Trailer'),
                    ('Tanker', 'Tanker'),
                ],
                attrs={'class': 'form-control'}
            ),
            'vehicle_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter capacity in bags',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Driver Name',
            'phone': 'Phone Number',
            'license_number': 'License Number',
            'vehicle_number': 'Vehicle Number',
            'vehicle_type': 'Vehicle Type',
            'vehicle_capacity': 'Vehicle Capacity (Bags)',
            'is_active': 'Active Status'
        }
        help_texts = {
            'phone': 'Format: +91XXXXXXXXXX',
            'license_number': 'Enter valid driving license number',
            'vehicle_capacity': 'Maximum bags the vehicle can carry',
            'is_active': 'Uncheck to mark driver as unavailable'
        }
    
    def clean_license_number(self):
        """
        Validate license number format and uniqueness
        """
        license_number = self.cleaned_data.get('license_number')
        
        # Check uniqueness (exclude current instance if updating)
        qs = Driver.objects.filter(license_number=license_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('This license number is already registered.')
        
        return license_number
    
    def clean_vehicle_capacity(self):
        """
        Validate vehicle capacity is positive
        """
        capacity = self.cleaned_data.get('vehicle_capacity')
        if capacity and capacity <= 0:
            raise forms.ValidationError('Vehicle capacity must be greater than 0.')
        return capacity
