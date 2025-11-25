from django.contrib import admin
from .models import Vendor, Driver, CementProduct, Order, OrderItem, Payment


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'phone', 'city', 'credit_limit', 'outstanding_balance', 'is_active']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'company_name', 'phone', 'email']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'vehicle_number', 'vehicle_type', 'vehicle_capacity', 'is_active']
    list_filter = ['is_active', 'vehicle_type']
    search_fields = ['name', 'phone', 'vehicle_number', 'license_number']


@admin.register(CementProduct)
class CementProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'weight_per_bag', 'price_per_bag', 'stock_quantity', 'is_low_stock', 'is_active']
    list_filter = ['grade', 'is_active']
    search_fields = ['name', 'grade']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'vendor', 'order_date', 'delivery_date', 'status', 'payment_status', 'total_amount', 'is_active']
    list_filter = ['status', 'payment_status', 'order_date', 'delivery_date']
    search_fields = ['order_number', 'vendor__name', 'vendor__company_name']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_date', 'amount', 'payment_type', 'reference_number']
    list_filter = ['payment_type', 'payment_date']
    search_fields = ['order__order_number', 'reference_number']
