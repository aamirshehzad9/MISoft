"""
UoM Conversion Service
Handles unit of measure conversions with support for multiple conversion types
"""
from decimal import Decimal
from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError
from products.models import UoMConversion, UnitOfMeasure, Product


class UoMConversionService:
    """
    Service for converting quantities between different units of measure
    Supports: Simple multiplier, Density-based, and Custom formula conversions
    """
    
    @staticmethod
    def convert(
        quantity: Decimal,
        from_uom: UnitOfMeasure,
        to_uom: UnitOfMeasure,
        product: Optional[Product] = None
    ) -> Dict[str, Any]:
        """
        Convert quantity from one UoM to another
        
        Args:
            quantity: Quantity to convert
            from_uom: Source unit of measure
            to_uom: Target unit of measure
            product: Product (required for density-based conversions)
            
        Returns:
            Dict with converted_quantity, conversion_rule, and metadata
            
        Raises:
            ValidationError: If conversion is not possible
        """
        # If same UoM, return as-is
        if from_uom == to_uom:
            return {
                'converted_quantity': quantity,
                'from_uom': from_uom.symbol,
                'to_uom': to_uom.symbol,
                'conversion_type': 'none',
                'conversion_rule': None
            }
        
        # Try to find direct conversion rule
        conversion = UoMConversionService._find_conversion_rule(from_uom, to_uom)
        
        if conversion:
            converted_qty = UoMConversionService._apply_conversion(
                quantity, conversion, product, reverse=False
            )
            return {
                'converted_quantity': converted_qty,
                'from_uom': from_uom.symbol,
                'to_uom': to_uom.symbol,
                'conversion_type': conversion.conversion_type,
                'conversion_rule': str(conversion),
                'multiplier': conversion.multiplier if conversion.conversion_type == 'simple' else None
            }
        
        # Try reverse conversion if bidirectional
        reverse_conversion = UoMConversionService._find_conversion_rule(to_uom, from_uom)
        
        if reverse_conversion and reverse_conversion.is_bidirectional:
            converted_qty = UoMConversionService._apply_conversion(
                quantity, reverse_conversion, product, reverse=True
            )
            return {
                'converted_quantity': converted_qty,
                'from_uom': from_uom.symbol,
                'to_uom': to_uom.symbol,
                'conversion_type': reverse_conversion.conversion_type,
                'conversion_rule': f"{str(reverse_conversion)} (reversed)",
                'multiplier': reverse_conversion.multiplier if reverse_conversion.conversion_type == 'simple' else None
            }
        
        # No conversion found
        raise ValidationError(
            f"No conversion rule found from {from_uom.symbol} to {to_uom.symbol}"
        )
    
    @staticmethod
    def _find_conversion_rule(from_uom: UnitOfMeasure, to_uom: UnitOfMeasure) -> Optional[UoMConversion]:
        """Find active conversion rule between two UoMs"""
        try:
            return UoMConversion.objects.get(
                from_uom=from_uom,
                to_uom=to_uom,
                is_active=True
            )
        except UoMConversion.DoesNotExist:
            return None
    
    @staticmethod
    def _apply_conversion(
        quantity: Decimal,
        conversion: UoMConversion,
        product: Optional[Product],
        reverse: bool = False
    ) -> Decimal:
        """
        Apply conversion rule to quantity
        
        Args:
            quantity: Quantity to convert
            conversion: Conversion rule to apply
            product: Product (required for density conversions)
            reverse: If True, apply reverse conversion
            
        Returns:
            Converted quantity
        """
        if conversion.conversion_type == 'simple':
            return UoMConversionService._simple_conversion(quantity, conversion, reverse)
        
        elif conversion.conversion_type == 'density':
            return UoMConversionService._density_conversion(quantity, conversion, product, reverse)
        
        elif conversion.conversion_type == 'formula':
            return UoMConversionService._formula_conversion(quantity, conversion, reverse)
        
        else:
            raise ValidationError(f"Unknown conversion type: {conversion.conversion_type}")
    
    @staticmethod
    def _simple_conversion(quantity: Decimal, conversion: UoMConversion, reverse: bool) -> Decimal:
        """
        Simple multiplier conversion
        Example: kg to g = multiply by 1000
        """
        if not conversion.multiplier:
            raise ValidationError("Multiplier is required for simple conversions")
        
        if reverse:
            # Reverse: divide instead of multiply
            return quantity / conversion.multiplier
        else:
            return quantity * conversion.multiplier
    
    @staticmethod
    def _density_conversion(
        quantity: Decimal,
        conversion: UoMConversion,
        product: Optional[Product],
        reverse: bool
    ) -> Decimal:
        """
        Density-based conversion (Volume ↔ Weight)
        Example: Liters to Kg using product density
        
        Formula:
        - Volume to Weight: weight = volume × density
        - Weight to Volume: volume = weight / density
        """
        if not product:
            raise ValidationError("Product is required for density-based conversions")
        
        if not product.density:
            raise ValidationError(f"Product {product.code} does not have density defined")
        
        # Determine conversion direction
        from_type = conversion.from_uom.uom_type
        to_type = conversion.to_uom.uom_type
        
        if reverse:
            # Swap types when reversing
            from_type, to_type = to_type, from_type
        
        if from_type == 'volume' and to_type == 'weight':
            # Volume to Weight: multiply by density
            return quantity * product.density
        
        elif from_type == 'weight' and to_type == 'volume':
            # Weight to Volume: divide by density
            if product.density == 0:
                raise ValidationError("Product density cannot be zero")
            return quantity / product.density
        
        else:
            raise ValidationError(
                f"Invalid density conversion: {from_type} to {to_type}"
            )
    
    @staticmethod
    def _formula_conversion(quantity: Decimal, conversion: UoMConversion, reverse: bool) -> Decimal:
        """
        Custom formula conversion
        Formula should be a Python expression using 'quantity' as variable
        
        Example formulas:
        - "quantity * 2.54" (inches to cm)
        - "quantity / 2.54" (cm to inches)
        - "(quantity - 32) * 5/9" (Fahrenheit to Celsius)
        """
        if not conversion.formula:
            raise ValidationError("Formula is required for formula conversions")
        
        if reverse:
            raise ValidationError(
                "Reverse formula conversions are not supported. "
                "Create a separate conversion rule for the reverse direction."
            )
        
        try:
            # Create safe evaluation environment
            safe_globals = {
                '__builtins__': {},
                'Decimal': Decimal,
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
            }
            
            safe_locals = {
                'quantity': float(quantity)
            }
            
            # Evaluate formula
            result = eval(conversion.formula, safe_globals, safe_locals)
            
            return Decimal(str(result))
        
        except Exception as e:
            raise ValidationError(f"Error evaluating formula: {str(e)}")
    
    @staticmethod
    def bulk_convert(
        conversions: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Perform multiple conversions in bulk
        
        Args:
            conversions: List of dicts with keys: quantity, from_uom_id, to_uom_id, product_id (optional)
            
        Returns:
            List of conversion results
        """
        results = []
        
        for conv in conversions:
            try:
                from_uom = UnitOfMeasure.objects.get(id=conv['from_uom_id'])
                to_uom = UnitOfMeasure.objects.get(id=conv['to_uom_id'])
                product = None
                
                if conv.get('product_id'):
                    product = Product.objects.get(id=conv['product_id'])
                
                result = UoMConversionService.convert(
                    quantity=Decimal(str(conv['quantity'])),
                    from_uom=from_uom,
                    to_uom=to_uom,
                    product=product
                )
                
                results.append({
                    'success': True,
                    **result
                })
            
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_data': conv
                })
        
        return results
    
    @staticmethod
    def get_available_conversions(from_uom: UnitOfMeasure) -> list[UoMConversion]:
        """
        Get all available conversions from a given UoM
        Includes both direct and bidirectional reverse conversions
        """
        # Direct conversions
        direct = list(UoMConversion.objects.filter(
            from_uom=from_uom,
            is_active=True
        ))
        
        # Reverse bidirectional conversions
        reverse = list(UoMConversion.objects.filter(
            to_uom=from_uom,
            is_active=True,
            is_bidirectional=True
        ))
        
        return direct + reverse
