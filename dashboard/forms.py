"""
Forms for order management using Django Forms with OOP
"""
from django import forms
from .models import Order, OrderItem, Vendor, Driver, CementProduct
from django.forms import inlineformset_factory


class OrderForm(forms.ModelForm):
    """
    Main order form with validation
    """
    
    class Meta:
        model = Order
        fields = [
            'vendor', 'driver', 'delivery_date', 'delivery_address',
            'discount_percent', 'tax_percent', 'payment_method', 'notes'
        ]
        widgets = {
            'vendor': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'driver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter delivery address'
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'value': '0'
            }),
            'tax_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'value': '18'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def clean_delivery_date(self):
        from django.utils import timezone
        delivery_date = self.cleaned_data.get('delivery_date')
        if delivery_date and delivery_date < timezone.now().date():
            raise forms.ValidationError("Delivery date cannot be in the past")
        return delivery_date


class OrderItemForm(forms.ModelForm):
    """
    Order item form for adding products
    """
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control product-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1',
                'value': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control price-input',
                'min': '0',
                'step': '0.01',
                'readonly': True
            }),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        
        if product and quantity > product.stock_quantity:
            raise forms.ValidationError(
                f"Insufficient stock. Available: {product.stock_quantity} bags"
            )
        return quantity


# Formset for multiple order items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)
