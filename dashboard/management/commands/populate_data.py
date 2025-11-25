"""
Management command to populate sample data
"""
from django.core.management.base import BaseCommand
from dashboard.models import Vendor, Driver, CementProduct
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create Vendors
        vendors_data = [
            {
                'name': 'Rajesh Kumar',
                'company_name': 'ABC Constructions Pvt Ltd',
                'email': 'rajesh@abcconstructions.com',
                'phone': '+919876543210',
                'address': '123, MG Road',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'pincode': '400001',
                'gst_number': 'GST123456789',
                'credit_limit': Decimal('500000'),
                'outstanding_balance': Decimal('125000')
            },
            {
                'name': 'Amit Sharma',
                'company_name': 'XYZ Builders',
                'email': 'amit@xyzbuilders.com',
                'phone': '+919876543211',
                'address': '456, Park Street',
                'city': 'Delhi',
                'state': 'Delhi',
                'pincode': '110001',
                'gst_number': 'GST987654321',
                'credit_limit': Decimal('750000'),
                'outstanding_balance': Decimal('200000')
            },
            {
                'name': 'Priya Patel',
                'company_name': 'PQR Developers',
                'email': 'priya@pqrdev.com',
                'phone': '+919876543212',
                'address': '789, Ring Road',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'pincode': '380001',
                'gst_number': 'GST456789123',
                'credit_limit': Decimal('600000'),
                'outstanding_balance': Decimal('150000')
            }
        ]
        
        for vendor_data in vendors_data:
            Vendor.objects.get_or_create(
                phone=vendor_data['phone'],
                defaults=vendor_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(vendors_data)} vendors'))
        
        # Create Drivers
        drivers_data = [
            {
                'name': 'Ramesh Singh',
                'phone': '+919876543220',
                'license_number': 'DL1234567890',
                'vehicle_number': 'MH-01-AB-1234',
                'vehicle_type': 'Truck',
                'vehicle_capacity': 500
            },
            {
                'name': 'Suresh Yadav',
                'phone': '+919876543221',
                'license_number': 'DL0987654321',
                'vehicle_number': 'DL-02-CD-5678',
                'vehicle_type': 'Truck',
                'vehicle_capacity': 600
            },
            {
                'name': 'Mahesh Patil',
                'phone': '+919876543222',
                'license_number': 'DL1122334455',
                'vehicle_number': 'GJ-03-EF-9012',
                'vehicle_type': 'Truck',
                'vehicle_capacity': 550
            }
        ]
        
        for driver_data in drivers_data:
            Driver.objects.get_or_create(
                license_number=driver_data['license_number'],
                defaults=driver_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(drivers_data)} drivers'))
        
        # Create Cement Products
        products_data = [
            {
                'name': 'Premium Cement',
                'grade': '43',
                'weight_per_bag': Decimal('50.00'),
                'price_per_bag': Decimal('350.00'),
                'stock_quantity': 5000,
                'reorder_level': 500
            },
            {
                'name': 'Premium Cement',
                'grade': '53',
                'weight_per_bag': Decimal('50.00'),
                'price_per_bag': Decimal('400.00'),
                'stock_quantity': 3500,
                'reorder_level': 400
            },
            {
                'name': 'PPC Cement',
                'grade': 'PPC',
                'weight_per_bag': Decimal('50.00'),
                'price_per_bag': Decimal('320.00'),
                'stock_quantity': 4200,
                'reorder_level': 450
            },
            {
                'name': 'PSC Cement',
                'grade': 'PSC',
                'weight_per_bag': Decimal('50.00'),
                'price_per_bag': Decimal('330.00'),
                'stock_quantity': 2800,
                'reorder_level': 350
            },
            {
                'name': 'OPC Cement',
                'grade': '33',
                'weight_per_bag': Decimal('50.00'),
                'price_per_bag': Decimal('310.00'),
                'stock_quantity': 1500,
                'reorder_level': 200
            }
        ]
        
        for product_data in products_data:
            CementProduct.objects.get_or_create(
                name=product_data['name'],
                grade=product_data['grade'],
                defaults=product_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(products_data)} products'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
