"""
URL configuration for dashboard app
"""
from django.urls import path
from .views import (
    DashboardHomeView, OrderCreateView, OrderDetailView,
    VendorListView, VendorCreateView, VendorUpdateView, VendorDeleteView,
    DriverListView, DriverCreateView, DriverUpdateView, DriverDeleteView,
    StockListView, StockUpdateView, ProductCreateView,
    PendingOrderListView, OrderStatusUpdateView,
    DailyDispatchView,
    FinanceView,
    AlertsView,
    SettingsView,
    SupportView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='home'),
    
    # Order URLs
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    
    # Vendor URLs
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    path('vendors/create/', VendorCreateView.as_view(), name='vendor_create'),
    path('vendors/<int:pk>/edit/', VendorUpdateView.as_view(), name='vendor_update'),
    path('vendors/<int:pk>/delete/', VendorDeleteView.as_view(), name='vendor_delete'),
    
    # Driver URLs
    path('drivers/', DriverListView.as_view(), name='driver_list'),
    path('drivers/create/', DriverCreateView.as_view(), name='driver_create'),
    path('drivers/<int:pk>/edit/', DriverUpdateView.as_view(), name='driver_update'),
    path('drivers/<int:pk>/delete/', DriverDeleteView.as_view(), name='driver_delete'),
    
    # Stock/Inventory URLs
    path('stock/', StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/update/', StockUpdateView.as_view(), name='stock_update'),
    path('stock/products/create/', ProductCreateView.as_view(), name='product_create'),
    
    # Pending Orders URLs
    path('orders/pending/', PendingOrderListView.as_view(), name='pending_orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    
    # Daily Dispatch URLs
    path('dispatch/', DailyDispatchView.as_view(), name='daily_dispatch'),
    
    # Finance Analytics
    path('finance/', FinanceView.as_view(), name='finance'),
    
    # Alerts & Notifications
    path('alerts/', AlertsView.as_view(), name='alerts'),
    
    # Settings
    path('settings/', SettingsView.as_view(), name='settings'),
    
    # Support & Help
    path('support/', SupportView.as_view(), name='support'),
]
