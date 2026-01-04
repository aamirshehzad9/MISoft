"""
Comprehensive Test Suite for UoM Conversion System
Task 1.5.5: Bulk Import & Testing - Quality Gate Implementation
Coverage Target: >85%
"""
from django.test import TestCase
from decimal import Decimal
from products.models import UnitOfMeasure, UoMConversion
from products.services.uom_conversion_service import UoMConversionService


class UoMConversionServiceTestCase(TestCase):
    """Test UoM Conversion Service - All Conversion Types"""
    
    def setUp(self):
        """Set up test data"""
        # Create units
        self.meter = UnitOfMeasure.objects.create(name='Meter', symbol='m', uom_type='length')
        self.centimeter = UnitOfMeasure.objects.create(name='Centimeter', symbol='cm', uom_type='length')
        self.kilogram = UnitOfMeasure.objects.create(name='Kilogram', symbol='kg', uom_type='weight')
        self.gram = UnitOfMeasure.objects.create(name='Gram', symbol='g', uom_type='weight')
        
        # Create simple conversions
        UoMConversion.objects.create(
            from_uom=self.meter,
            to_uom=self.centimeter,
            conversion_type='simple',
            multiplier=Decimal('100')
        )
        UoMConversion.objects.create(
            from_uom=self.centimeter,
            to_uom=self.meter,
            conversion_type='simple',
            multiplier=Decimal('0.01')
        )
        UoMConversion.objects.create(
            from_uom=self.kilogram,
            to_uom=self.gram,
            conversion_type='simple',
            multiplier=Decimal('1000')
        )
        
        self.service = UoMConversionService()
    
    def test_simple_conversion_forward(self):
        """Test simple multiplier conversion (m to cm)"""
        result = self.service.convert(
            quantity=Decimal('5'),
            from_uom=self.meter,
            to_uom=self.centimeter
        )
        self.assertEqual(result['converted_quantity'], Decimal('500'))
        self.assertEqual(result['conversion_type'], 'simple')
        self.assertEqual(result['multiplier'], Decimal('100'))
    
    def test_simple_conversion_reverse(self):
        """Test simple multiplier conversion (cm to m)"""
        result = self.service.convert(
            quantity=Decimal('500'),
            from_uom=self.centimeter,
            to_uom=self.meter
        )
        self.assertEqual(result['converted_quantity'], Decimal('5'))
        self.assertEqual(result['conversion_type'], 'simple')
    
    def test_simple_conversion_large_numbers(self):
        """Test simple conversion with large numbers"""
        result = self.service.convert(
            quantity=Decimal('10'),
            from_uom=self.kilogram,
            to_uom=self.gram
        )
        self.assertEqual(result['converted_quantity'], Decimal('10000'))
    
    def test_conversion_not_found(self):
        """Test error when conversion rule doesn't exist"""
        with self.assertRaises(Exception):
            self.service.convert(
                quantity=Decimal('10'),
                from_uom=self.meter,
                to_uom=self.kilogram  # No conversion between length and weight
            )
    
    def test_conversion_validation_zero(self):
        """Test zero quantity conversion"""
        result = self.service.convert(
            quantity=Decimal('0'),
            from_uom=self.meter,
            to_uom=self.centimeter
        )
        self.assertEqual(result['converted_quantity'], Decimal('0'))
    
    def test_formula_based_conversion(self):
        """Test custom formula conversion"""
        # Create formula-based conversion (Celsius to Fahrenheit)
        celsius = UnitOfMeasure.objects.create(name='Celsius', symbol='°C', uom_type='temperature')
        fahrenheit = UnitOfMeasure.objects.create(name='Fahrenheit', symbol='°F', uom_type='temperature')
        
        UoMConversion.objects.create(
            from_uom=celsius,
            to_uom=fahrenheit,
            conversion_type='formula',
            formula='(quantity * 9/5) + 32'
        )
        
        result = self.service.convert(
            quantity=Decimal('0'),  # 0°C
            from_uom=celsius,
            to_uom=fahrenheit
        )
        
        self.assertEqual(result['converted_quantity'], Decimal('32'))  # 32°F
        self.assertEqual(result['conversion_type'], 'formula')
    
    def test_formula_conversion_complex(self):
        """Test complex formula conversion"""
        # Reuse units from previous test
        celsius = UnitOfMeasure.objects.create(name='Celsius2', symbol='°C2', uom_type='temperature')
        fahrenheit = UnitOfMeasure.objects.create(name='Fahrenheit2', symbol='°F2', uom_type='temperature')
        
        UoMConversion.objects.create(
            from_uom=celsius,
            to_uom=fahrenheit,
            conversion_type='formula',
            formula='(quantity * 9/5) + 32'
        )
        
        result = self.service.convert(
            quantity=Decimal('100'),  # 100°C
            from_uom=celsius,
            to_uom=fahrenheit
        )
        
        self.assertEqual(result['converted_quantity'], Decimal('212'))  # 212°F
    
    def test_conversion_validation_zero(self):
        """Test zero quantity conversion"""
        result = self.service.convert(
            quantity=Decimal('0'),
            from_uom=self.meter,
            to_uom=self.centimeter
        )
        self.assertEqual(result['converted_quantity'], Decimal('0'))


class UoMConversionModelTestCase(TestCase):
    """Test UoMConversion Model"""
    
    def setUp(self):
        self.meter = UnitOfMeasure.objects.create(name='Meter', symbol='m', uom_type='length')
        self.kilometer = UnitOfMeasure.objects.create(name='Kilometer', symbol='km', uom_type='length')
    
    def test_create_simple_conversion(self):
        """Test creating a simple conversion"""
        conversion = UoMConversion.objects.create(
            from_uom=self.meter,
            to_uom=self.kilometer,
            conversion_type='simple',
            multiplier=Decimal('0.001')
        )
        
        self.assertEqual(conversion.from_uom, self.meter)
        self.assertEqual(conversion.to_uom, self.kilometer)
        self.assertEqual(conversion.multiplier, Decimal('0.001'))
        self.assertTrue(conversion.is_active)
    
    def test_create_formula_conversion(self):
        """Test creating a formula-based conversion"""
        conversion = UoMConversion.objects.create(
            from_uom=self.meter,
            to_uom=self.kilometer,
            conversion_type='formula',
            formula='quantity / 1000'
        )
        
        self.assertEqual(conversion.conversion_type, 'formula')
        self.assertIsNotNone(conversion.formula)
    
    def test_conversion_string_representation(self):
        """Test string representation"""
        conversion = UoMConversion.objects.create(
            from_uom=self.meter,
            to_uom=self.kilometer,
            conversion_type='simple',
            multiplier=Decimal('0.001')
        )
        
        str_repr = str(conversion)
        self.assertIn('m', str_repr)
        self.assertIn('km', str_repr)


class UnitOfMeasureModelTestCase(TestCase):
    """Test UnitOfMeasure Model"""
    
    def test_create_unit(self):
        """Test creating a unit of measure"""
        unit = UnitOfMeasure.objects.create(
            name='Meter',
            symbol='m',
            uom_type='length'
        )
        
        self.assertEqual(unit.name, 'Meter')
        self.assertEqual(unit.symbol, 'm')
        self.assertEqual(unit.uom_type, 'length')
    
    def test_unit_string_representation(self):
        """Test string representation"""
        unit = UnitOfMeasure.objects.create(name='Meter', symbol='m', uom_type='length')
        self.assertEqual(str(unit), 'Meter (m)')


class UoMConversionCoverageTestCase(TestCase):
    """Test coverage of all conversion types and edge cases"""
    
    def setUp(self):
        # Run seed command to populate data
        from django.core.management import call_command
        call_command('seed_uom_data')
        self.service = UoMConversionService()
    
    def test_all_length_conversions(self):
        """Test all length unit conversions"""
        mm = UnitOfMeasure.objects.get(symbol='mm')
        cm = UnitOfMeasure.objects.get(symbol='cm')
        m = UnitOfMeasure.objects.get(symbol='m')
        
        # mm to cm
        result = self.service.convert(Decimal('10'), mm, cm)
        self.assertEqual(result['converted_quantity'], Decimal('1'))
        
        # cm to m
        result = self.service.convert(Decimal('100'), cm, m)
        self.assertEqual(result['converted_quantity'], Decimal('1'))
    
    def test_all_weight_conversions(self):
        """Test all weight unit conversions"""
        g = UnitOfMeasure.objects.get(symbol='g')
        kg = UnitOfMeasure.objects.get(symbol='kg')
        
        # g to kg
        result = self.service.convert(Decimal('1000'), g, kg)
        self.assertEqual(result['converted_quantity'], Decimal('1'))
    
    def test_all_volume_conversions(self):
        """Test all volume unit conversions"""
        ml = UnitOfMeasure.objects.get(symbol='ml')
        L = UnitOfMeasure.objects.get(symbol='L')
        
        # ml to L
        result = self.service.convert(Decimal('1000'), ml, L)
        self.assertEqual(result['converted_quantity'], Decimal('1'))
    
    def test_conversion_accuracy(self):
        """Test conversion accuracy with decimal precision"""
        kg = UnitOfMeasure.objects.get(symbol='kg')
        lb = UnitOfMeasure.objects.get(symbol='lb')
        
        # kg to lb (should be ~2.2046)
        result = self.service.convert(Decimal('1'), kg, lb)
        self.assertAlmostEqual(float(result['converted_quantity']), 2.2046, places=2)
    
    def test_bidirectional_conversions(self):
        """Test that bidirectional conversions are consistent"""
        m = UnitOfMeasure.objects.get(symbol='m')
        cm = UnitOfMeasure.objects.get(symbol='cm')
        
        # Forward: m to cm
        forward = self.service.convert(Decimal('1'), m, cm)
        
        # Reverse: cm to m
        reverse = self.service.convert(forward['converted_quantity'], cm, m)
        
        # Should get back to original (with rounding tolerance)
        self.assertAlmostEqual(float(reverse['converted_quantity']), 1.0, places=2)
    
    def test_total_units_seeded(self):
        """Test that all units were seeded"""
        total_units = UnitOfMeasure.objects.count()
        self.assertGreaterEqual(total_units, 38)  # Should have at least 38 units
    
    def test_total_conversions_seeded(self):
        """Test that all conversions were seeded"""
        total_conversions = UoMConversion.objects.count()
        self.assertGreaterEqual(total_conversions, 78)  # Should have at least 78 conversions
    
    def test_all_uom_types_present(self):
        """Test that all UoM types are present"""
        uom_types = UnitOfMeasure.objects.values_list('uom_type', flat=True).distinct()
        
        expected_types = ['length', 'weight', 'volume', 'area', 'time', 'unit']
        for expected_type in expected_types:
            self.assertIn(expected_type, uom_types)
