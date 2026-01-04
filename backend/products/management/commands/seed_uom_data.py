"""
Django management command to seed standard Units of Measure and Conversion Rules
Task 1.5.5: Bulk Import & Testing
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import UnitOfMeasure, UoMConversion
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds standard Units of Measure and Conversion Rules for UoM Converter'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing UoM data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing UoM data...'))
            UoMConversion.objects.all().delete()
            UnitOfMeasure.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared!'))

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Units of Measure...'))
        
        with transaction.atomic():
            # Create all units
            units_created = self.create_units()
            
            # Create conversion rules
            conversions_created = self.create_conversions()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully seeded {units_created} units and {conversions_created} conversion rules!'
        ))

    def create_units(self):
        """Create standard units of measure"""
        units_data = [
            # Length Units
            {'name': 'Millimeter', 'symbol': 'mm', 'uom_type': 'length'},
            {'name': 'Centimeter', 'symbol': 'cm', 'uom_type': 'length'},
            {'name': 'Meter', 'symbol': 'm', 'uom_type': 'length'},
            {'name': 'Kilometer', 'symbol': 'km', 'uom_type': 'length'},
            {'name': 'Inch', 'symbol': 'in', 'uom_type': 'length'},
            {'name': 'Foot', 'symbol': 'ft', 'uom_type': 'length'},
            {'name': 'Yard', 'symbol': 'yd', 'uom_type': 'length'},
            {'name': 'Mile', 'symbol': 'mi', 'uom_type': 'length'},
            
            # Weight/Mass Units
            {'name': 'Milligram', 'symbol': 'mg', 'uom_type': 'weight'},
            {'name': 'Gram', 'symbol': 'g', 'uom_type': 'weight'},
            {'name': 'Kilogram', 'symbol': 'kg', 'uom_type': 'weight'},
            {'name': 'Metric Ton', 'symbol': 't', 'uom_type': 'weight'},
            {'name': 'Ounce', 'symbol': 'oz', 'uom_type': 'weight'},
            {'name': 'Pound', 'symbol': 'lb', 'uom_type': 'weight'},
            {'name': 'Ton', 'symbol': 'ton', 'uom_type': 'weight'},
            
            # Volume Units
            {'name': 'Milliliter', 'symbol': 'ml', 'uom_type': 'volume'},
            {'name': 'Liter', 'symbol': 'L', 'uom_type': 'volume'},
            {'name': 'Cubic Meter', 'symbol': 'm³', 'uom_type': 'volume'},
            {'name': 'Fluid Ounce', 'symbol': 'fl oz', 'uom_type': 'volume'},
            {'name': 'Pint', 'symbol': 'pt', 'uom_type': 'volume'},
            {'name': 'Quart', 'symbol': 'qt', 'uom_type': 'volume'},
            {'name': 'Gallon', 'symbol': 'gal', 'uom_type': 'volume'},
            
            # Area Units
            {'name': 'Square Meter', 'symbol': 'm²', 'uom_type': 'area'},
            {'name': 'Square Kilometer', 'symbol': 'km²', 'uom_type': 'area'},
            {'name': 'Hectare', 'symbol': 'ha', 'uom_type': 'area'},
            {'name': 'Square Foot', 'symbol': 'ft²', 'uom_type': 'area'},
            {'name': 'Acre', 'symbol': 'acre', 'uom_type': 'area'},
            
            # Time Units
            {'name': 'Second', 'symbol': 's', 'uom_type': 'time'},
            {'name': 'Minute', 'symbol': 'min', 'uom_type': 'time'},
            {'name': 'Hour', 'symbol': 'h', 'uom_type': 'time'},
            {'name': 'Day', 'symbol': 'day', 'uom_type': 'time'},
            {'name': 'Week', 'symbol': 'week', 'uom_type': 'time'},
            {'name': 'Month', 'symbol': 'month', 'uom_type': 'time'},
            {'name': 'Year', 'symbol': 'year', 'uom_type': 'time'},
            
            # Quantity Units
            {'name': 'Unit', 'symbol': 'pcs', 'uom_type': 'unit'},
            {'name': 'Dozen', 'symbol': 'doz', 'uom_type': 'unit'},
            {'name': 'Gross', 'symbol': 'gross', 'uom_type': 'unit'},
            {'name': 'Hundred', 'symbol': '100', 'uom_type': 'unit'},
            {'name': 'Thousand', 'symbol': '1000', 'uom_type': 'unit'},
        ]
        
        count = 0
        for unit_data in units_data:
            unit, created = UnitOfMeasure.objects.get_or_create(
                symbol=unit_data['symbol'],
                defaults=unit_data
            )
            if created:
                count += 1
                self.stdout.write(f'  Created: {unit.name} ({unit.symbol})')
            else:
                self.stdout.write(self.style.WARNING(f'  Exists: {unit.name} ({unit.symbol})'))
        
        return count

    def create_conversions(self):
        """Create standard conversion rules"""
        self.stdout.write(self.style.MIGRATE_HEADING('\nCreating Conversion Rules...'))
        
        conversions_data = [
            # Length Conversions
            ('mm', 'cm', Decimal('0.1')),
            ('cm', 'm', Decimal('0.01')),
            ('m', 'km', Decimal('0.001')),
            ('in', 'ft', Decimal('0.0833')),
            ('ft', 'yd', Decimal('0.3333')),
            ('yd', 'mi', Decimal('0.0006')),
            ('in', 'cm', Decimal('2.54')),
            ('ft', 'm', Decimal('0.3048')),
            ('mi', 'km', Decimal('1.6093')),
            
            # Weight Conversions
            ('mg', 'g', Decimal('0.001')),
            ('g', 'kg', Decimal('0.001')),
            ('kg', 't', Decimal('0.001')),
            ('oz', 'lb', Decimal('0.0625')),
            ('lb', 'ton', Decimal('0.0005')),
            ('g', 'oz', Decimal('0.0353')),
            ('kg', 'lb', Decimal('2.2046')),
            ('t', 'ton', Decimal('1.1023')),
            
            # Volume Conversions
            ('ml', 'L', Decimal('0.001')),
            ('L', 'm³', Decimal('0.001')),
            ('fl oz', 'pt', Decimal('0.0625')),
            ('pt', 'qt', Decimal('0.5')),
            ('qt', 'gal', Decimal('0.25')),
            ('ml', 'fl oz', Decimal('0.0338')),
            ('L', 'gal', Decimal('0.2642')),
            
            # Area Conversions
            ('m²', 'km²', Decimal('0.0001')),
            ('m²', 'ha', Decimal('0.0001')),
            ('ft²', 'acre', Decimal('0.0001')),
            ('m²', 'ft²', Decimal('10.7639')),
            ('ha', 'acre', Decimal('2.4711')),
            
            # Time Conversions
            ('s', 'min', Decimal('0.0167')),
            ('min', 'h', Decimal('0.0167')),
            ('h', 'day', Decimal('0.0417')),
            ('day', 'week', Decimal('0.1429')),
            ('week', 'month', Decimal('0.2301')),
            ('month', 'year', Decimal('0.0833')),
            
            # Quantity Conversions
            ('pcs', 'doz', Decimal('0.0833')),
            ('doz', 'gross', Decimal('0.0833')),
            ('pcs', '100', Decimal('0.01')),
            ('100', '1000', Decimal('0.1')),
        ]
        
        count = 0
        for from_symbol, to_symbol, multiplier in conversions_data:
            try:
                from_uom = UnitOfMeasure.objects.get(symbol=from_symbol)
                to_uom = UnitOfMeasure.objects.get(symbol=to_symbol)
                
                # Create forward conversion
                conv_forward, created_forward = UoMConversion.objects.get_or_create(
                    from_uom=from_uom,
                    to_uom=to_uom,
                    defaults={
                        'conversion_type': 'simple',
                        'multiplier': multiplier,
                        'is_active': True
                    }
                )
                
                if created_forward:
                    count += 1
                    self.stdout.write(f'  ✓ {from_symbol} → {to_symbol} (×{multiplier})')
                
                # Create reverse conversion
                reverse_multiplier = (Decimal('1') / multiplier).quantize(Decimal('0.0001'))
                conv_reverse, created_reverse = UoMConversion.objects.get_or_create(
                    from_uom=to_uom,
                    to_uom=from_uom,
                    defaults={
                        'conversion_type': 'simple',
                        'multiplier': reverse_multiplier,
                        'is_active': True
                    }
                )
                
                if created_reverse:
                    count += 1
                    self.stdout.write(f'  ✓ {to_symbol} → {from_symbol} (×{reverse_multiplier:.6f})')
                    
            except UnitOfMeasure.DoesNotExist as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Missing unit: {e}'))
        
        return count
