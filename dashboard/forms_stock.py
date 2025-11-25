"""
Stock Management Forms
"""
from django import forms
from .models import CementProduct


class StockUpdateForm(forms.ModelForm):
    """
    Form for updating stock quantities
    """
    adjustment_type = forms.ChoiceField(
        choices=[
            ('add', 'Add Stock (Purchase/Production)'),
            ('remove', 'Remove Stock (Damage/Loss)'),
            ('set', 'Set Stock (Manual Adjustment)')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'adjustmentType'
        }),
        initial='add'
    )
    
    adjustment_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity',
            'id': 'adjustmentQuantity'
        }),
        label='Quantity'
    )
    
    adjustment_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
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
                'class': 'form-control',
                'placeholder': 'Product Name',
                'readonly': 'readonly'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }),
            'weight_per_bag': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'price_per_bag': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
        labels = {
            'name': 'Product Name',
            'grade': 'Grade',
            'weight_per_bag': 'Weight per Bag (KG)',
            'price_per_bag': 'Price per Bag (₹)',
            'reorder_level': 'Reorder Level (Bags)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Make grade field show current value but disabled
            self.fields['grade'].widget.attrs.pop('disabled', None)
            self.fields['grade'].widget.attrs['readonly'] = 'readonly'
    
    def clean_adjustment_quantity(self):
        """
        Validate adjustment quantity
        """
        quantity = self.cleaned_data.get('adjustment_quantity')
        adjustment_type = self.data.get('adjustment_type')
        
        if adjustment_type == 'remove':
            current_stock = self.instance.stock_quantity if self.instance else 0
            if quantity > current_stock:
                raise forms.ValidationError(
                    f'Cannot remove {quantity} bags. Only {current_stock} bags available in stock.'
                )
        
        return quantity


class ProductCreateForm(forms.ModelForm):
    """
    Form for creating new cement products
    """
    initial_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
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
                'class': 'form-control',
                'placeholder': 'e.g., UltraTech Cement'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'weight_per_bag': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'value': '50.00'
            }),
            'price_per_bag': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Price per bag'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
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
