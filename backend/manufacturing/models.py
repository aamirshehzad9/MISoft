from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import CustomUser
from products.models import Product, UnitOfMeasure

class WorkCenter(models.Model):
    """Manufacturing work centers/stations"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Capacity
    capacity_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Production capacity per hour")
    capacity_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='work_centers')
    
    # Costing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost per hour")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class BillOfMaterials(models.Model):
    """Bill of Materials - Recipe/Formula for manufacturing"""
    
    BOM_TYPE_CHOICES = [
        ('manufacturing', 'Manufacturing'),
        ('assembly', 'Assembly'),
        ('disassembly', 'Disassembly'),
    ]
    
    # Product Information
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='boms', 
                               limit_choices_to={'is_manufactured': True})
    version = models.CharField(max_length=20, default='1.0')
    bom_type = models.CharField(max_length=20, choices=BOM_TYPE_CHOICES, default='manufacturing')
    
    # Quantity
    quantity = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal('0.0001'))],
                                   help_text="Output quantity for this BOM")
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='boms')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default BOM for this product")
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_boms')
    
    class Meta:
        ordering = ['-is_default', 'product', 'version']
        verbose_name = "Bill of Materials"
        verbose_name_plural = "Bills of Materials"
        unique_together = [['product', 'version']]
    
    def __str__(self):
        return f"BOM-{self.product.code}-v{self.version}"
    
    @property
    def total_material_cost(self):
        """Calculate total material cost"""
        return sum(item.total_cost for item in self.items.all())


class BOMItem(models.Model):
    """Individual items/materials in a BOM"""
    
    ITEM_TYPE_CHOICES = [
        ('raw_material', 'Raw Material'),
        ('semi_finished', 'Semi-Finished'),
        ('consumable', 'Consumable'),
    ]
    
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='raw_material')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='bom_items')
    
    # Quantity
    quantity = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal('0.0001'))])
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='bom_items')
    
    # Scrap/Waste
    scrap_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                          validators=[MinValueValidator(0)],
                                          help_text="Expected scrap/waste percentage")
    
    # Sequence
    sequence = models.IntegerField(default=10, help_text="Order of addition in manufacturing")
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['sequence', 'product']
    
    def __str__(self):
        return f"{self.product.code} - {self.quantity} {self.uom.symbol}"
    
    @property
    def quantity_with_scrap(self):
        """Calculate quantity including scrap"""
        return self.quantity * (1 + self.scrap_percentage / 100)
    
    @property
    def total_cost(self):
        """Calculate total cost for this item"""
        return self.quantity_with_scrap * self.product.standard_cost


class BOMOperation(models.Model):
    """Manufacturing operations/routing for BOM"""
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, related_name='operations')
    sequence = models.IntegerField(default=10)
    operation_name = models.CharField(max_length=100)
    work_center = models.ForeignKey(WorkCenter, on_delete=models.PROTECT, related_name='operations')
    
    # Time
    setup_time_minutes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    run_time_minutes = models.DecimalField(max_digits=8, decimal_places=2, default=0, 
                                          help_text="Time per unit")
    
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.sequence}. {self.operation_name}"
    
    @property
    def total_time_minutes(self):
        """Calculate total time for BOM quantity"""
        return self.setup_time_minutes + (self.run_time_minutes * float(self.bom.quantity))
    
    @property
    def operation_cost(self):
        """Calculate operation cost"""
        return (self.total_time_minutes / 60) * float(self.work_center.hourly_rate)


class ProductionOrder(models.Model):
    """Production/Work Orders"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('released', 'Released'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Order Information
    order_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='production_orders')
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.PROTECT, related_name='production_orders')
    
    # Quantity
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal('0.0001'))])
    produced_quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    rejected_quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='production_orders')
    
    # Dates
    planned_start_date = models.DateTimeField()
    planned_end_date = models.DateTimeField()
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.IntegerField(default=5, help_text="1=Highest, 10=Lowest")
    
    # Batch Information
    batch_number = models.CharField(max_length=50, blank=True)
    lot_number = models.CharField(max_length=50, blank=True)
    
    # Costing
    estimated_material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_overhead_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    actual_material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_overhead_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_production_orders')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.product.name}"
    
    @property
    def total_estimated_cost(self):
        return self.estimated_material_cost + self.estimated_labor_cost + self.estimated_overhead_cost
    
    @property
    def total_actual_cost(self):
        return self.actual_material_cost + self.actual_labor_cost + self.actual_overhead_cost
    
    @property
    def completion_percentage(self):
        if self.planned_quantity > 0:
            return (self.produced_quantity / self.planned_quantity) * 100
        return 0


class MaterialConsumption(models.Model):
    """Track material consumption in production"""
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='material_consumptions')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='material_consumptions')
    
    # Quantity
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=4)
    consumed_quantity = models.DecimalField(max_digits=12, decimal_places=4)
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='material_consumptions')
    
    # Batch/Lot tracking
    batch_number = models.CharField(max_length=50, blank=True)
    lot_number = models.CharField(max_length=50, blank=True)
    
    # Costing
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    consumed_at = models.DateTimeField(auto_now_add=True)
    consumed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='material_consumptions')
    
    class Meta:
        ordering = ['consumed_at']
    
    def __str__(self):
        return f"{self.product.code} - {self.consumed_quantity} {self.uom.symbol}"
    
    def save(self, *args, **kwargs):
        self.total_cost = self.consumed_quantity * self.unit_cost
        super().save(*args, **kwargs)


class QualityCheck(models.Model):
    """Quality control checkpoints"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('on_hold', 'On Hold'),
    ]
    
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='quality_checks')
    check_name = models.CharField(max_length=100)
    check_type = models.CharField(max_length=50, blank=True, help_text="e.g., Visual, Chemical, Physical")
    
    # Parameters
    parameter_name = models.CharField(max_length=100, blank=True)
    expected_value = models.CharField(max_length=100, blank=True)
    actual_value = models.CharField(max_length=100, blank=True)
    tolerance = models.CharField(max_length=50, blank=True)
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    
    # Metadata
    checked_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='quality_checks')
    
    class Meta:
        ordering = ['checked_at']
    
    def __str__(self):
        return f"{self.check_name} - {self.status}"


class ProductionDowntime(models.Model):
    """Track production downtime"""
    
    DOWNTIME_TYPE_CHOICES = [
        ('breakdown', 'Machine Breakdown'),
        ('maintenance', 'Scheduled Maintenance'),
        ('material_shortage', 'Material Shortage'),
        ('power_failure', 'Power Failure'),
        ('other', 'Other'),
    ]
    
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='downtimes')
    work_center = models.ForeignKey(WorkCenter, on_delete=models.PROTECT, related_name='downtimes')
    
    downtime_type = models.CharField(max_length=30, choices=DOWNTIME_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    description = models.TextField()
    resolution = models.TextField(blank=True)
    
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='reported_downtimes')
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.downtime_type} - {self.work_center.name}"
    
    @property
    def duration_minutes(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0
