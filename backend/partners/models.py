from django.db import models
from accounts.models import CustomUser

class BusinessPartner(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    
    # Contact Details
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Pakistan')
    
    # Partner Type (Can be both customer and vendor)
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    
    # Financial Information
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_terms_days = models.IntegerField(default=30, help_text="Payment terms in days")
    
    # Tax Information
    tax_id = models.CharField(max_length=50, blank=True, help_text="Tax/GST Number")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_partners')
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_customer', 'is_vendor']),
        ]
    
    def __str__(self):
        partner_type = []
        if self.is_customer:
            partner_type.append('Customer')
        if self.is_vendor:
            partner_type.append('Vendor')
        type_str = '/'.join(partner_type) if partner_type else 'Partner'
        return f"{self.name} ({type_str})"
    
    @property
    def partner_type_display(self):
        """Returns a human-readable partner type"""
        if self.is_customer and self.is_vendor:
            return "Customer & Vendor"
        elif self.is_customer:
            return "Customer"
        elif self.is_vendor:
            return "Vendor"
        return "Partner"
