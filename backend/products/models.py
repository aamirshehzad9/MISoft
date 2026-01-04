from django.db import models
from accounts.models import CustomUser
from partners.models import BusinessPartner

class ProductCategory(models.Model):
    """Hierarchical product categories"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """Returns full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class UnitOfMeasure(models.Model):
    """Units of measurement (kg, liters, pieces, etc.)"""
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    uom_type = models.CharField(max_length=20, choices=[
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ('length', 'Length'),
        ('unit', 'Unit/Piece'),
        ('time', 'Time'),
    ])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Product(models.Model):
    """Main product model for raw materials and finished goods"""
    
    PRODUCT_TYPE_CHOICES = [
        ('raw_material', 'Raw Material'),
        ('finished_good', 'Finished Good'),
        ('semi_finished', 'Semi-Finished'),
        ('consumable', 'Consumable'),
        ('service', 'Service'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, help_text="SKU/Product Code")
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    qr_code = models.CharField(max_length=200, blank=True)
    
    # Classification
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    # Description
    description = models.TextField(blank=True)
    specifications = models.TextField(blank=True, help_text="Technical specifications")
    
    # Units
    base_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='products_base')
    purchase_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='products_purchase', null=True, blank=True)
    sales_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='products_sales', null=True, blank=True)
    
    # Conversion Factors
    purchase_to_base_factor = models.DecimalField(max_digits=10, decimal_places=4, default=1.0, help_text="Purchase UOM to Base UOM")
    sales_to_base_factor = models.DecimalField(max_digits=10, decimal_places=4, default=1.0, help_text="Sales UOM to Base UOM")
    
    # Inventory Management
    track_inventory = models.BooleanField(default=True)
    track_batches = models.BooleanField(default=False, help_text="Enable batch/lot tracking")
    track_serial_numbers = models.BooleanField(default=False)
    
    # Stock Levels
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_point = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Storage
    storage_location = models.CharField(max_length=100, blank=True)
    shelf_life_days = models.IntegerField(null=True, blank=True, help_text="Shelf life in days")
    
    # Pricing
    standard_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Standard/Average cost")
    last_purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Suppliers
    preferred_vendor = models.ForeignKey(BusinessPartner, on_delete=models.SET_NULL, null=True, blank=True, 
                                        limit_choices_to={'is_vendor': True}, related_name='preferred_products')
    
    # Tax & Compliance
    tax_category = models.CharField(max_length=50, blank=True)
    hs_code = models.CharField(max_length=20, blank=True, help_text="Harmonized System Code for import/export")
    
    # Manufacturing
    is_manufactured = models.BooleanField(default=False)
    manufacturing_lead_time_days = models.IntegerField(default=0)
    
    # Density for UoM conversions (Task 1.5.2)
    density = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text="Product density for volume-weight conversions (e.g., kg/liter)"
    )
    density_uom = models.ForeignKey(
        UnitOfMeasure, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='density_products',
        help_text="Reference UoM for density measurement"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_purchasable = models.BooleanField(default=True)
    is_saleable = models.BooleanField(default=True)
    
    # Images & Documents
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_products')
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def current_stock(self):
        """Calculate current stock from inventory transactions"""
        # This will be implemented when we create inventory transactions
        return 0


class ProductVariant(models.Model):
    """Product variants (size, color, grade, etc.)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=100, help_text="e.g., Size: Large, Color: Red")
    variant_code = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    
    # Pricing (can override parent product)
    price_adjustment = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Price difference from base product")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['variant_name']
    
    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"


class UoMConversion(models.Model):
    """
    Unit of Measure Conversion Rules
    Supports multiple conversion types for complex manufacturing scenarios
    """
    
    CONVERSION_TYPES = [
        ('simple', 'Simple Multiplier'),
        ('density', 'Density-based (Volume ↔ Weight)'),
        ('formula', 'Custom Formula'),
    ]
    
    from_uom = models.ForeignKey(
        UnitOfMeasure, 
        on_delete=models.CASCADE, 
        related_name='conversions_from',
        help_text="Source unit of measure"
    )
    to_uom = models.ForeignKey(
        UnitOfMeasure, 
        on_delete=models.CASCADE, 
        related_name='conversions_to',
        help_text="Target unit of measure"
    )
    conversion_type = models.CharField(
        max_length=20, 
        choices=CONVERSION_TYPES,
        default='simple',
        help_text="Type of conversion calculation"
    )
    multiplier = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text="Multiplier for simple conversions (e.g., 1000 for kg to g)"
    )
    formula = models.TextField(
        null=True, 
        blank=True,
        help_text="Python expression for custom conversions. Use 'quantity' as variable."
    )
    is_active = models.BooleanField(default=True)
    is_bidirectional = models.BooleanField(
        default=True,
        help_text="If true, reverse conversion is automatically available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['from_uom', 'to_uom']
        unique_together = ['from_uom', 'to_uom']
        verbose_name = "UoM Conversion"
        verbose_name_plural = "UoM Conversions"
    
    def __str__(self):
        return f"{self.from_uom.symbol} → {self.to_uom.symbol} ({self.get_conversion_type_display()})"
    
    def clean(self):
        """Validate conversion rules"""
        from django.core.exceptions import ValidationError
        
        # Validate that from_uom and to_uom are different
        if self.from_uom == self.to_uom:
            raise ValidationError("Cannot create conversion from a UoM to itself")
        
        # Validate multiplier for simple conversions
        if self.conversion_type == 'simple' and not self.multiplier:
            raise ValidationError("Multiplier is required for simple conversions")
        
        # Validate formula for custom conversions
        if self.conversion_type == 'formula' and not self.formula:
            raise ValidationError("Formula is required for custom formula conversions")
        
        # Validate density conversions require compatible UoM types
        if self.conversion_type == 'density':
            valid_combinations = [
                ('volume', 'weight'),
                ('weight', 'volume')
            ]
            if (self.from_uom.uom_type, self.to_uom.uom_type) not in valid_combinations:
                raise ValidationError(
                    "Density-based conversions require volume ↔ weight UoM types"
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
