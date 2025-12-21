from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, UnitOfMeasure, Product, ProductVariant
from .serializers import (ProductCategorySerializer, UnitOfMeasureSerializer,
                          ProductSerializer, ProductListSerializer, ProductVariantSerializer)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']

class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['uom_type', 'is_active']
    search_fields = ['name', 'symbol']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'base_uom', 'preferred_vendor').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product_type', 'category', 'is_active', 'is_manufactured', 'track_batches']
    search_fields = ['name', 'code', 'barcode', 'description']
    ordering_fields = ['name', 'code', 'selling_price', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def raw_materials(self, request):
        """Get only raw materials"""
        products = self.queryset.filter(product_type='raw_material', is_active=True)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def finished_goods(self, request):
        """Get only finished goods"""
        products = self.queryset.filter(product_type='finished_good', is_active=True)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products below reorder point"""
        # This will be implemented when we add inventory transactions
        return Response([])
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['variant_name', 'variant_code', 'barcode']
