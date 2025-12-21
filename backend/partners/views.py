from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import BusinessPartner
from .serializers import BusinessPartnerSerializer, BusinessPartnerListSerializer

class BusinessPartnerViewSet(viewsets.ModelViewSet):
    queryset = BusinessPartner.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_customer', 'is_vendor', 'is_active']
    search_fields = ['name', 'company_name', 'email', 'phone', 'tax_id']
    ordering_fields = ['name', 'created_at', 'outstanding_balance']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BusinessPartnerListSerializer
        return BusinessPartnerSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """Get only customers"""
        customers = self.queryset.filter(is_customer=True, is_active=True)
        serializer = BusinessPartnerListSerializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vendors(self, request):
        """Get only vendors"""
        vendors = self.queryset.filter(is_vendor=True, is_active=True)
        serializer = BusinessPartnerListSerializer(vendors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status"""
        partner = self.get_object()
        partner.is_active = not partner.is_active
        partner.save()
        serializer = self.get_serializer(partner)
        return Response(serializer.data)
