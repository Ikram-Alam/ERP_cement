"""
Forms for order management using Django Forms with OOP
"""
from django import forms
from .models import Order, OrderItem, Vendor, Driver, CementProduct
from django.forms import inlineformset_factory


class VendorForm(forms.ModelForm):
    """
    Vendor creation and update form with validation
    """
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'company_name', 'email', 'phone',
            'address', 'city', 'state', 'pincode',
            'gst_number', 'credit_limit', 'outstanding_balance', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter vendor/customer name',
                'required': True
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter company name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+91 1234567890',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Enter complete street address',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City name',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'State name',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '123456',
                'required': True,
                'maxlength': '10'
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '22AAAAA0000A1Z5',
                'maxlength': '15'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'step': '0.01',
                'value': '0',
                'placeholder': '0.00'
            }),
            'outstanding_balance': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'step': '0.01',
                'value': '0',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
        labels = {
            'name': 'Vendor/Customer Name',
            'company_name': 'Company Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'address': 'Street Address',
            'city': 'City',
            'state': 'State',
            'pincode': 'PIN Code',
            'gst_number': 'GST Number',
            'credit_limit': 'Credit Limit',
            'outstanding_balance': 'Outstanding Balance',
            'is_active': 'Active Status'
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # No validation - accept any phone number format
        return phone
    
    def clean_gst_number(self):
        gst = self.cleaned_data.get('gst_number')
        if gst:
            # Basic GST format validation (15 characters)
            if len(gst) != 15:
                raise forms.ValidationError("GST number must be exactly 15 characters")
            if not gst[:2].isdigit():
                raise forms.ValidationError("GST number must start with 2 digits (state code)")
        return gst.upper() if gst else gst
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        # Remove spaces for validation
        cleaned_pincode = pincode.replace(' ', '')
        if not cleaned_pincode.isdigit():
            raise forms.ValidationError("PIN code must contain only digits")
        if len(cleaned_pincode) != 6:
            raise forms.ValidationError("PIN code must be 6 digits")
        return pincode
    
    def clean(self):
        cleaned_data = super().clean()
        credit_limit = cleaned_data.get('credit_limit', 0)
        outstanding = cleaned_data.get('outstanding_balance', 0)
        
        if outstanding and credit_limit and outstanding > credit_limit:
            raise forms.ValidationError(
                "Outstanding balance cannot exceed credit limit"
            )
        
        return cleaned_data


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
