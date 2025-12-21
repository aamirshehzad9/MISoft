from rest_framework import serializers
from .models import BusinessPartner

class BusinessPartnerSerializer(serializers.ModelSerializer):
    partner_type_display = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessPartner
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'outstanding_balance')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None
    
    def validate(self, data):
        # Ensure at least one partner type is selected
        if not data.get('is_customer') and not data.get('is_vendor'):
            raise serializers.ValidationError(
                "Partner must be either a customer, vendor, or both."
            )
        return data

class BusinessPartnerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    partner_type_display = serializers.ReadOnlyField()
    
    class Meta:
        model = BusinessPartner
        fields = ('id', 'name', 'company_name', 'email', 'phone', 'is_customer', 
                  'is_vendor', 'partner_type_display', 'outstanding_balance', 'is_active')
