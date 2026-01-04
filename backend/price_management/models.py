from django.db import models
from products.models import Product
from partners.models import BusinessPartner

class PriceRule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_rules')
    rule_name = models.CharField(max_length=200)
    priority = models.IntegerField(default=10)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    customer = models.ForeignKey(BusinessPartner, on_delete=models.CASCADE, null=True, blank=True, related_name='price_rules')
    customer_category = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    min_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) 
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.rule_name} - {self.product.code}"
    
    class Meta:
        ordering = ['-priority', '-valid_from']
