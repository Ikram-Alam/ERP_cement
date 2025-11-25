"""
Dashboard models using proper OOP principles
"""
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class Vendor(BaseModel):
    """
    Vendor/Customer model for cement buyers
    """
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number")]
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    gst_number = models.CharField(max_length=15, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
    
    def __str__(self):
        return f"{self.name} - {self.company_name or 'Individual'}"
    
    @property
    def available_credit(self):
        return self.credit_limit - self.outstanding_balance


class Driver(BaseModel):
    """
    Driver model for delivery personnel
    """
    name = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    license_number = models.CharField(max_length=50, unique=True)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50, default='Truck')
    vehicle_capacity = models.IntegerField(help_text="Capacity in bags")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.vehicle_number}"


class CementProduct(BaseModel):
    """
    Cement product/grade model
    """
    GRADE_CHOICES = [
        ('33', 'Grade 33'),
        ('43', 'Grade 43'),
        ('53', 'Grade 53'),
        ('PPC', 'Portland Pozzolana Cement'),
        ('PSC', 'Portland Slag Cement'),
    ]
    
    name = models.CharField(max_length=200)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    weight_per_bag = models.DecimalField(max_digits=5, decimal_places=2, default=50.00, help_text="Weight in KG")
    price_per_bag = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=100, help_text="Alert when stock falls below this")
    
    class Meta:
        ordering = ['grade', 'name']
        verbose_name = 'Cement Product'
        verbose_name_plural = 'Cement Products'
    
    def __str__(self):
        return f"{self.name} - {self.get_grade_display()}"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level
    
    @property
    def stock_value(self):
        return self.stock_quantity * self.price_per_bag


class Order(BaseModel):
    """
    Main order model
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online', 'Online Transfer'),
        ('credit', 'Credit'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='orders')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)  # GST
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"{self.order_number} - {self.vendor.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            today = timezone.now()
            date_str = today.strftime('%Y%m%d')
            last_order = Order.objects.filter(
                order_number__startswith=f'ORD-{date_str}'
            ).order_by('order_number').last()
            
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f'ORD-{date_str}-{new_number:04d}'
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.discount_amount = (self.subtotal * self.discount_percent) / 100
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = (taxable_amount * self.tax_percent) / 100
        self.total_amount = taxable_amount + self.tax_amount
        self.save()
    
    @property
    def balance_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def total_bags(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def is_delayed(self):
        if self.delivery_date and self.status not in ['delivered', 'cancelled']:
            return self.delivery_date < timezone.now().date()
        return False


class OrderItem(BaseModel):
    """
    Order line items
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(CementProduct, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update order totals
        self.order.calculate_totals()


class Payment(BaseModel):
    """
    Payment transactions for orders
    """
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online', 'Online Transfer'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.amount} for {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update order paid amount
        self.order.paid_amount = sum(p.amount for p in self.order.payments.all())
        
        # Update payment status
        if self.order.paid_amount >= self.order.total_amount:
            self.order.payment_status = 'paid'
        elif self.order.paid_amount > 0:
            self.order.payment_status = 'partial'
        else:
            self.order.payment_status = 'unpaid'
        
        self.order.save()
