from rest_framework import serializers
from .models import PriceRule

class PriceRuleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = PriceRule
        fields = '__all__'

class PriceCalculationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, default=1)
    date = serializers.DateField(required=False, allow_null=True)
