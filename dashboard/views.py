"""
Dashboard views using Class-Based Views for proper OOP structure
"""
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from typing import Dict, Any
from .models import Order, OrderItem, Vendor, Driver, CementProduct
from .forms import OrderForm, OrderItemFormSet
from .forms_vendor import VendorForm
from .forms_driver import DriverForm
from .forms_stock import StockUpdateForm, ProductCreateForm


class BaseDashboardView(TemplateView):
    """
    Base view class for all dashboard views.
    Implements common functionality using OOP principles.
    """
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Add common context data for all dashboard views
        """
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context


class DashboardHomeView(BaseDashboardView):
    """
    Home/Landing page view with dashboard statistics
    """
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Provide dashboard statistics and alerts
        """
        from datetime import date, timedelta
        from django.db.models import Sum, Count, Q
        from decimal import Decimal
        
        context = super().get_context_data(**kwargs)
        
        # Get today's date range
        today = date.today()
        yesterday = today - timedelta(days=1)
        last_month = today - timedelta(days=30)
        
        # Calculate real statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(
            status__in=['pending', 'confirmed', 'processing']
        ).count()
        
        delivered_today = Order.objects.filter(
            order_date__date=today,
            status='delivered'
        ).count()
        
        # Stock calculation
        total_stock = CementProduct.objects.aggregate(
            total=Sum('stock_quantity')
        )['total'] or 0
        
        low_stock_alerts = CementProduct.objects.filter(
            stock_quantity__lt=500  # Alert threshold
        ).count()
        
        # Revenue today
        revenue_today = Order.objects.filter(
            order_date__date=today,
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        revenue_yesterday = Order.objects.filter(
            order_date__date=yesterday,
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Revenue comparison
        if revenue_yesterday > 0:
            revenue_change = ((float(revenue_today) - float(revenue_yesterday)) / float(revenue_yesterday)) * 100
        else:
            revenue_change = 0
        
        # Active drivers
        active_drivers = Driver.objects.filter(is_active=True).count()
        
        # Delayed orders
        delayed_orders = Order.objects.filter(
            status__in=['confirmed', 'processing', 'dispatched'],
            delivery_date__lt=today
        ).count()
        
        # Orders this month vs last month
        orders_this_month = Order.objects.filter(
            order_date__date__gte=last_month
        ).count()
        orders_last_month = Order.objects.filter(
            order_date__date__gte=today - timedelta(days=60),
            order_date__date__lt=last_month
        ).count()
        
        if orders_last_month > 0:
            orders_change = ((orders_this_month - orders_last_month) / orders_last_month) * 100
        else:
            orders_change = 0
        
        context['stats'] = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_today': delivered_today,
            'total_stock': total_stock,
            'low_stock_alerts': low_stock_alerts,
            'delayed_orders': delayed_orders,
            'revenue_today': float(revenue_today),
            'revenue_change': revenue_change,
            'active_drivers': active_drivers,
            'orders_change': orders_change,
        }
        
        # Real alerts based on system status
        alerts = []
        
        # Low stock alerts
        low_stock_products = CementProduct.objects.filter(stock_quantity__lt=500).order_by('stock_quantity')[:3]
        for product in low_stock_products:
            alerts.append({
                'type': 'warning',
                'icon': 'exclamation-triangle',
                'message': f'Stock running low for {product.name} ({product.stock_quantity} bags remaining)',
                'time': 'Now'
            })
        
        # Delayed orders alert
        if delayed_orders > 0:
            alerts.append({
                'type': 'danger',
                'icon': 'clock',
                'message': f'{delayed_orders} order{"s" if delayed_orders > 1 else ""} delayed past delivery date',
                'time': 'Now'
            })
        
        # Recent pending orders
        recent_pending = Order.objects.filter(status='pending').order_by('-order_date').first()
        if recent_pending:
            time_diff = (today - recent_pending.order_date.date()).days
            if time_diff == 0:
                time_str = 'Today'
            elif time_diff == 1:
                time_str = 'Yesterday'
            else:
                time_str = f'{time_diff} days ago'
            
            alerts.append({
                'type': 'info',
                'icon': 'info-circle',
                'message': f'New order {recent_pending.order_number} awaiting confirmation',
                'time': time_str
            })
        
        context['alerts'] = alerts[:5]  # Limit to 5 alerts
        
        # Recent deliveries - real data
        recent_deliveries = Order.objects.filter(
            status__in=['delivered', 'dispatched']
        ).select_related('vendor').order_by('-order_date')[:8]
        
        deliveries_list = []
        for order in recent_deliveries:
            total_bags = sum(item.quantity for item in order.items.all())
            deliveries_list.append({
                'order_id': order.order_number,
                'vendor': order.vendor.name,
                'bags': total_bags,
                'status': order.get_status_display(),
                'order_pk': order.pk,
            })
        
        context['recent_deliveries'] = deliveries_list
        
        # Weekly revenue data for chart
        weekly_revenue = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_revenue = Order.objects.filter(
                order_date__date=day,
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            weekly_revenue.append({
                'date': day.strftime('%a'),
                'revenue': float(day_revenue)
            })
        
        # Monthly revenue for comparison
        monthly_revenue = []
        for i in range(11, -1, -1):
            month_date = today - timedelta(days=i*30)
            month_start = date(month_date.year, month_date.month, 1)
            if month_date.month == 12:
                month_end = date(month_date.year, 12, 31)
            else:
                month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
            
            month_rev = Order.objects.filter(
                order_date__date__gte=month_start,
                order_date__date__lte=month_end,
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            monthly_revenue.append({
                'month': month_start.strftime('%b'),
                'revenue': float(month_rev)
            })
        
        # Convert to JSON for JavaScript
        import json
        context['weekly_revenue_json'] = json.dumps(weekly_revenue)
        context['monthly_revenue_json'] = json.dumps(monthly_revenue)
        
        return context


class OrderCreateView(BaseDashboardView):
    """
    Create new order with line items using proper OOP
    """
    template_name = 'dashboard/order_create.html'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Provide form and related data
        """
        context = super().get_context_data(**kwargs)
        
        # Get or create forms
        if self.request.POST:
            context['form'] = OrderForm(self.request.POST)
        else:
            context['form'] = OrderForm()
        
        # Get all vendors, drivers, and products for dropdowns
        context['vendors'] = Vendor.objects.filter(is_active=True)
        context['drivers'] = Driver.objects.filter(is_active=True)
        
        # Get products and format for JavaScript
        products = CementProduct.objects.filter(is_active=True)
        context['products'] = products
        
        # Format products for JSON
        import json
        products_json = []
        for p in products:
            products_json.append({
                'id': p.id,
                'name': p.name,
                'grade': p.grade,
                'price': float(p.price_per_bag),
                'stock': p.stock_quantity
            })
        context['products_json'] = json.dumps(products_json)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Handle form submission
        """
        from decimal import Decimal
        
        # Get form data
        vendor_id = request.POST.get('vendor')
        driver_id = request.POST.get('driver')
        delivery_date = request.POST.get('delivery_date')
        delivery_address = request.POST.get('delivery_address')
        discount_percent = request.POST.get('discount_percent', 0)
        tax_percent = request.POST.get('tax_percent', 18)
        payment_method = request.POST.get('payment_method', 'cash')
        notes = request.POST.get('notes', '')
        
        # Get order items from POST data
        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('unit_price[]')
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    vendor_id=vendor_id,
                    driver_id=driver_id if driver_id else None,
                    delivery_date=delivery_date if delivery_date else None,
                    delivery_address=delivery_address,
                    discount_percent=Decimal(str(discount_percent)) if discount_percent else Decimal('0'),
                    tax_percent=Decimal(str(tax_percent)) if tax_percent else Decimal('18'),
                    payment_method=payment_method,
                    notes=notes,
                    status='pending'
                )
                
                # Create order items
                for product_id, quantity, price in zip(products, quantities, prices):
                    if product_id and quantity and price:
                        OrderItem.objects.create(
                            order=order,
                            product_id=product_id,
                            quantity=int(quantity),
                            unit_price=Decimal(str(price))
                        )
                
                # Calculate totals
                order.calculate_totals()
                
                messages.success(request, f'Order {order.order_number} created successfully!')
                return redirect('dashboard:home')
                
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return self.get(request, *args, **kwargs)


# ========================================
# Vendor Views
# ========================================

class VendorListView(ListView):
    """
    Display list of all vendors with search and filter
    """
    model = Vendor
    template_name = 'dashboard/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Filter vendors based on search query
        """
        queryset = Vendor.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        
        # Filter by active status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add common context from BaseDashboardView
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        # Add vendor-specific context
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['total_vendors'] = Vendor.objects.count()
        context['active_vendors'] = Vendor.objects.filter(is_active=True).count()
        return context


class VendorCreateView(CreateView):
    """
    Create a new vendor
    """
    model = Vendor
    form_class = VendorForm
    template_name = 'dashboard/vendor_form.html'
    success_url = reverse_lazy('dashboard:vendor_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Vendor "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class VendorUpdateView(UpdateView):
    """
    Update existing vendor
    """
    model = Vendor
    form_class = VendorForm
    template_name = 'dashboard/vendor_form.html'
    success_url = reverse_lazy('dashboard:vendor_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Vendor "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class VendorDeleteView(DeleteView):
    """
    Soft delete vendor (set is_active=False)
    """
    model = Vendor
    success_url = reverse_lazy('dashboard:vendor_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(request, f'Vendor "{self.object.name}" deactivated successfully!')
        return redirect(self.success_url)


# ========================================
# Driver Views
# ========================================

class DriverListView(ListView):
    """
    Display list of all drivers with search and filter
    """
    model = Driver
    template_name = 'dashboard/driver_list.html'
    context_object_name = 'drivers'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Filter drivers based on search query
        """
        queryset = Driver.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(license_number__icontains=search_query) |
                Q(vehicle_number__icontains=search_query) |
                Q(vehicle_type__icontains=search_query)
            )
        
        # Filter by active status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by vehicle type
        vehicle_filter = self.request.GET.get('vehicle_type', '')
        if vehicle_filter:
            queryset = queryset.filter(vehicle_type=vehicle_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add common context
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        # Add driver-specific context
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['vehicle_filter'] = self.request.GET.get('vehicle_type', '')
        context['total_drivers'] = Driver.objects.count()
        context['active_drivers'] = Driver.objects.filter(is_active=True).count()
        context['vehicle_types'] = Driver.objects.values_list('vehicle_type', flat=True).distinct()
        return context


class DriverCreateView(CreateView):
    """
    Create a new driver
    """
    model = Driver
    form_class = DriverForm
    template_name = 'dashboard/driver_form.html'
    success_url = reverse_lazy('dashboard:driver_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Driver "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class DriverUpdateView(UpdateView):
    """
    Update existing driver
    """
    model = Driver
    form_class = DriverForm
    template_name = 'dashboard/driver_form.html'
    success_url = reverse_lazy('dashboard:driver_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Driver "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class DriverDeleteView(DeleteView):
    """
    Soft delete driver (set is_active=False)
    """
    model = Driver
    success_url = reverse_lazy('dashboard:driver_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(request, f'Driver "{self.object.name}" marked as unavailable!')
        return redirect(self.success_url)


# ========================================
# Stock/Inventory Views
# ========================================

class StockListView(ListView):
    """
    Display warehouse stock/inventory with statistics
    """
    model = CementProduct
    template_name = 'dashboard/stock_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Filter products based on search and stock status
        """
        queryset = CementProduct.objects.all().order_by('grade', 'name')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(grade__icontains=search_query)
            )
        
        # Filter by grade
        grade_filter = self.request.GET.get('grade', '')
        if grade_filter:
            queryset = queryset.filter(grade=grade_filter)
        
        # Filter by stock status
        stock_filter = self.request.GET.get('stock_status', '')
        if stock_filter == 'low':
            # Products with stock at or below reorder level
            queryset = [p for p in queryset if p.is_low_stock]
        elif stock_filter == 'out':
            queryset = queryset.filter(stock_quantity=0)
        elif stock_filter == 'available':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add common context
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        # Calculate warehouse statistics
        all_products = CementProduct.objects.all()
        
        total_bags = sum(p.stock_quantity for p in all_products)
        total_value = sum(float(p.stock_value) for p in all_products)
        low_stock_count = sum(1 for p in all_products if p.is_low_stock and p.stock_quantity > 0)
        out_of_stock_count = all_products.filter(stock_quantity=0).count()
        
        context['warehouse_stats'] = {
            'total_products': all_products.count(),
            'total_bags': total_bags,
            'total_value': total_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
        }
        
        # Add filter context
        context['search_query'] = self.request.GET.get('search', '')
        context['grade_filter'] = self.request.GET.get('grade', '')
        context['stock_filter'] = self.request.GET.get('stock_status', '')
        context['grade_choices'] = CementProduct.GRADE_CHOICES
        
        return context


class StockUpdateView(UpdateView):
    """
    Update stock quantity for a product
    """
    model = CementProduct
    form_class = StockUpdateForm
    template_name = 'dashboard/stock_update.html'
    success_url = reverse_lazy('dashboard:stock_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        context['current_stock'] = self.object.stock_quantity
        return context
    
    def form_valid(self, form):
        # Get adjustment details
        adjustment_type = self.request.POST.get('adjustment_type')
        adjustment_quantity = int(self.request.POST.get('adjustment_quantity', 0))
        
        # Update stock based on adjustment type
        if adjustment_type == 'add':
            form.instance.stock_quantity += adjustment_quantity
            messages.success(
                self.request,
                f'Added {adjustment_quantity} bags. New stock: {form.instance.stock_quantity} bags'
            )
        elif adjustment_type == 'remove':
            form.instance.stock_quantity -= adjustment_quantity
            messages.success(
                self.request,
                f'Removed {adjustment_quantity} bags. New stock: {form.instance.stock_quantity} bags'
            )
        elif adjustment_type == 'set':
            old_stock = self.object.stock_quantity
            form.instance.stock_quantity = adjustment_quantity
            messages.success(
                self.request,
                f'Stock updated from {old_stock} to {adjustment_quantity} bags'
            )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductCreateView(CreateView):
    """
    Create a new cement product
    """
    model = CementProduct
    form_class = ProductCreateForm
    template_name = 'dashboard/product_create.html'
    success_url = reverse_lazy('dashboard:stock_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        return context
    
    def form_valid(self, form):
        # Set initial stock from form
        initial_stock = form.cleaned_data.get('initial_stock', 0)
        form.instance.stock_quantity = initial_stock
        
        messages.success(
            self.request,
            f'Product "{form.instance.name}" created with {initial_stock} bags in stock!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


# ========================================
# Pending Orders Views
# ========================================

class PendingOrderListView(ListView):
    """
    Display pending/active orders (not delivered or cancelled)
    """
    model = Order
    template_name = 'dashboard/pending_orders.html'
    context_object_name = 'orders'
    paginate_by = 15
    
    def get_queryset(self):
        """
        Filter orders by status - show pending, confirmed, processing, dispatched
        """
        queryset = Order.objects.select_related('vendor', 'driver').prefetch_related('items').filter(
            status__in=['pending', 'confirmed', 'processing', 'dispatched']
        ).order_by('-order_date')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(vendor__name__icontains=search_query) |
                Q(vendor__company_name__icontains=search_query) |
                Q(delivery_address__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment status
        payment_filter = self.request.GET.get('payment_status', '')
        if payment_filter:
            queryset = queryset.filter(payment_status=payment_filter)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        if date_from:
            queryset = queryset.filter(order_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(order_date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add common context
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        # Calculate statistics for pending orders
        all_pending = Order.objects.filter(
            status__in=['pending', 'confirmed', 'processing', 'dispatched']
        )
        
        context['order_stats'] = {
            'total_pending': all_pending.count(),
            'pending_count': all_pending.filter(status='pending').count(),
            'confirmed_count': all_pending.filter(status='confirmed').count(),
            'processing_count': all_pending.filter(status='processing').count(),
            'dispatched_count': all_pending.filter(status='dispatched').count(),
            'total_value': sum(float(o.total_amount) for o in all_pending),
        }
        
        # Add filter context
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['payment_filter'] = self.request.GET.get('payment_status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['status_choices'] = [
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('processing', 'Processing'),
            ('dispatched', 'Dispatched'),
        ]
        context['payment_choices'] = Order.PAYMENT_STATUS_CHOICES
        
        return context


class OrderStatusUpdateView(UpdateView):
    """
    Quick update order status
    """
    model = Order
    fields = ['status']
    success_url = reverse_lazy('dashboard:pending_orders')
    
    def form_valid(self, form):
        old_status = Order.objects.get(pk=self.object.pk).status
        new_status = form.cleaned_data['status']
        
        messages.success(
            self.request,
            f'Order {self.object.order_number} status updated from "{old_status}" to "{new_status}"'
        )
        return super().form_valid(form)


class OrderDetailView(TemplateView):
    """
    Display detailed order information
    """
    template_name = 'dashboard/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('pk')
        order = Order.objects.select_related('vendor', 'driver').prefetch_related('items__product').get(pk=order_id)
        
        context['order'] = order
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        return context


# ========================================
# Daily Dispatch Views
# ========================================

class DailyDispatchView(ListView):
    """
    Display daily dispatch/delivery tracking for supply chain management
    """
    model = Order
    template_name = 'dashboard/daily_dispatch.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Filter orders by dispatch/delivery status
        """
        from datetime import date, timedelta
        
        queryset = Order.objects.select_related('vendor', 'driver').prefetch_related('items').filter(
            status__in=['dispatched', 'delivered']
        ).order_by('-order_date')
        
        # Date filter - default to today
        selected_date = self.request.GET.get('date', '')
        if selected_date:
            queryset = queryset.filter(order_date__date=selected_date)
        else:
            # Default to today's dispatches
            today = date.today()
            queryset = queryset.filter(order_date__date=today)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(vendor__name__icontains=search_query) |
                Q(driver__name__icontains=search_query) |
                Q(driver__vehicle_number__icontains=search_query)
            )
        
        # Filter by status (dispatched or delivered)
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by driver
        driver_filter = self.request.GET.get('driver', '')
        if driver_filter:
            queryset = queryset.filter(driver_id=driver_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        from datetime import date, timedelta
        
        context = super().get_context_data(**kwargs)
        # Add common context
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        # Get selected date or default to today
        selected_date_str = self.request.GET.get('date', '')
        if selected_date_str:
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = date.today()
        
        context['selected_date'] = selected_date
        
        # Calculate dispatch statistics for selected date
        daily_orders = Order.objects.filter(
            order_date__date=selected_date,
            status__in=['dispatched', 'delivered']
        )
        
        total_bags = 0
        for order in daily_orders:
            for item in order.items.all():
                total_bags += item.quantity
        
        context['dispatch_stats'] = {
            'total_dispatches': daily_orders.count(),
            'dispatched_count': daily_orders.filter(status='dispatched').count(),
            'delivered_count': daily_orders.filter(status='delivered').count(),
            'total_bags': total_bags,
            'total_value': sum(float(o.total_amount) for o in daily_orders),
            'active_drivers': daily_orders.values('driver').distinct().count(),
        }
        
        # Add filter context
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['driver_filter'] = self.request.GET.get('driver', '')
        context['all_drivers'] = Driver.objects.filter(is_active=True)
        
        # Quick date navigation
        context['yesterday'] = selected_date - timedelta(days=1)
        context['tomorrow'] = selected_date + timedelta(days=1)
        context['today'] = date.today()
        
        return context


# ========================================
# Finance/Analytics Views
# ========================================

class FinanceView(TemplateView):
    """
    Finance dashboard with analytics, revenue, expenses, and profit tracking
    """
    template_name = 'dashboard/finance.html'
    
    def get_context_data(self, **kwargs):
        from datetime import date, timedelta
        from django.db.models import Sum, Count, Avg
        from decimal import Decimal
        
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        # Date range filters
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        # Default to current month if no dates provided
        if not date_from or not date_to:
            today = date.today()
            date_from = date(today.year, today.month, 1).strftime('%Y-%m-%d')
            # Last day of current month
            if today.month == 12:
                date_to = date(today.year, 12, 31).strftime('%Y-%m-%d')
            else:
                date_to = date(today.year, today.month + 1, 1) - timedelta(days=1)
                date_to = date_to.strftime('%Y-%m-%d')
        
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        # Filter orders by date range
        orders = Order.objects.filter(
            order_date__date__gte=date_from,
            order_date__date__lte=date_to
        )
        
        # Calculate key financial metrics
        total_revenue = orders.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_orders = orders.count()
        delivered_orders = orders.filter(status='delivered').count()
        pending_revenue = orders.filter(
            status__in=['pending', 'confirmed', 'processing', 'dispatched']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Payment analytics
        total_paid = orders.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')
        outstanding = float(total_revenue) - float(total_paid)
        
        # Average order value
        avg_order_value = orders.filter(status='delivered').aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0')
        
        # Top products by revenue
        from django.db.models import F
        top_products = OrderItem.objects.filter(
            order__order_date__date__gte=date_from,
            order__order_date__date__lte=date_to,
            order__status='delivered'
        ).values(
            'product__name',
            'product__grade'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_revenue')[:5]
        
        # Top vendors by revenue
        top_vendors = orders.filter(status='delivered').values(
            'vendor__name',
            'vendor__company_name'
        ).annotate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')[:5]
        
        # Monthly revenue trend (last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):
            month_date = date.today() - timedelta(days=i*30)
            month_start = date(month_date.year, month_date.month, 1)
            if month_date.month == 12:
                month_end = date(month_date.year, 12, 31)
            else:
                month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
            
            month_revenue = Order.objects.filter(
                order_date__date__gte=month_start,
                order_date__date__lte=month_end,
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(month_revenue)
            })
        
        # Order status breakdown
        status_breakdown = []
        for status_code, status_label in Order.STATUS_CHOICES:
            count = orders.filter(status=status_code).count()
            if count > 0:
                status_breakdown.append({
                    'status': status_label,
                    'count': count
                })
        
        # Payment status breakdown
        payment_breakdown = []
        for status_code, status_label in Order.PAYMENT_STATUS_CHOICES:
            count = orders.filter(payment_status=status_code).count()
            amount = orders.filter(payment_status=status_code).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            if count > 0:
                payment_breakdown.append({
                    'status': status_label,
                    'count': count,
                    'amount': float(amount)
                })
        
        # Daily revenue trend for selected period
        from datetime import datetime
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        daily_revenue = []
        
        current_date = start_date
        while current_date <= end_date:
            day_revenue = Order.objects.filter(
                order_date__date=current_date,
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            daily_revenue.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'revenue': float(day_revenue)
            })
            current_date += timedelta(days=1)
        
        # Compile all data
        context['finance_data'] = {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'pending_revenue': float(pending_revenue),
            'total_paid': float(total_paid),
            'outstanding': outstanding,
            'avg_order_value': float(avg_order_value),
            'collection_rate': (float(total_paid) / float(total_revenue) * 100) if total_revenue > 0 else 0,
        }
        
        context['top_products'] = top_products
        context['top_vendors'] = top_vendors
        context['monthly_data'] = monthly_data
        context['status_breakdown'] = status_breakdown
        context['payment_breakdown'] = payment_breakdown
        context['daily_revenue'] = daily_revenue
        
        # Convert to JSON for JavaScript charts
        import json
        context['monthly_data_json'] = json.dumps(monthly_data)
        context['status_breakdown_json'] = json.dumps(status_breakdown)
        context['payment_breakdown_json'] = json.dumps(payment_breakdown)
        context['daily_revenue_json'] = json.dumps(daily_revenue)
        
        return context


# ========================================
# Alerts/Notifications View
# ========================================

class AlertsView(TemplateView):
    """
    Static alerts and notifications page
    """
    template_name = 'dashboard/alerts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        return context


# ========================================
# Settings View
# ========================================

class SettingsView(TemplateView):
    """
    Static settings and configuration page
    """
    template_name = 'dashboard/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        return context


# ========================================
# Support/Help View
# ========================================

class SupportView(TemplateView):
    """
    Static support and help center page
    """
    template_name = 'dashboard/support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = 'CemERP'
        context['company_name'] = 'Cement Industry Management'
        
        return context





