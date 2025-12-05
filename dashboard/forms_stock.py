""" 
Stock Management Forms
"""
from django import forms
from .models import CementProduct


class StockUpdateForm(forms.ModelForm):
    """
    Form for updating stock quantities - No strict validations
    """
    adjustment_type = forms.ChoiceField(
        choices=[
            ('add', 'Add Stock (Purchase/Production)'),
            ('remove', 'Remove Stock (Damage/Loss)'),
            ('set', 'Set Stock (Manual Adjustment)')
        ],
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'adjustmentType'
        }),
        initial='add'
    )
    
    adjustment_quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter quantity',
            'id': 'adjustmentQuantity'
        }),
        label='Quantity'
    )
    
    adjustment_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Reason for stock adjustment (optional)',
            'rows': 3
        }),
        label='Reason/Notes'
    )
    
    class Meta:
        model = CementProduct
        fields = ['name', 'grade', 'weight_per_bag', 'price_per_bag', 'reorder_level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Product Name',
                'readonly': 'readonly'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-input',
                'disabled': 'disabled'
            }),
            'weight_per_bag': forms.NumberInput(attrs={
                'class': 'form-input',
                'readonly': 'readonly'
            }),
            'price_per_bag': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-input'
            })
        }
        labels = {
            'name': 'Product Name',
            'grade': 'Grade',
            'weight_per_bag': 'Weight per Bag (KG)',
            'price_per_bag': 'Price per Bag (₹)',
            'reorder_level': 'Reorder Level (Bags)'
        }
class ProductCreateForm(forms.ModelForm):
    """
    Form for creating new cement products - No validations
    """
    initial_stock = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Initial stock quantity'
        }),
        label='Initial Stock Quantity',
        help_text='Number of bags to add initially'
    )
    
    class Meta:
        model = CementProduct
        fields = ['name', 'grade', 'weight_per_bag', 'price_per_bag', 'reorder_level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., UltraTech Cement'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-input'
            }),
            'weight_per_bag': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'value': '50.00'
            }),
            'price_per_bag': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Price per bag'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'value': '100'
            })
        }
        labels = {
            'name': 'Product Name',
            'grade': 'Cement Grade',
            'weight_per_bag': 'Weight per Bag (KG)',
            'price_per_bag': 'Price per Bag (₹)',
            'reorder_level': 'Reorder Level (Bags)'
        }
        help_texts = {
            'reorder_level': 'Alert will be shown when stock falls below this level'
        }
