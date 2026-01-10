"""
UoM Conversion API Views
REST API endpoints for unit of measure conversions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from django.core.exceptions import ValidationError

from products.models import UoMConversion, UnitOfMeasure, Product, ProductVariant
from products.services.uom_conversion_service import UoMConversionService
from .serializers import (
    UoMConversionSerializer, UnitOfMeasureSerializer, 
    ProductSerializer, ProductVariantQuickCreateSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    """
    queryset = Product.objects.select_related(
        'category', 'base_uom', 'purchase_uom', 'sales_uom', 
        'preferred_vendor', 'density_uom', 'created_by'
    ).filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'base_uom', 'is_active', 'product_type']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'standard_cost', 'selling_price']
    ordering = ['name']



class UoMConversionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UoM Conversion CRUD operations
    """
    queryset = UoMConversion.objects.all()
    serializer_class = UoMConversionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['from_uom', 'to_uom', 'conversion_type', 'is_active']
    search_fields = ['from_uom__name', 'to_uom__name']
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """
        Convert quantity from one UoM to another
        
        POST /api/products/uom-conversions/convert/
        Body: {
            "quantity": "10.5",
            "from_uom_id": 1,
            "to_uom_id": 2,
            "product_id": 5  // optional, required for density conversions
        }
        """
        try:
            quantity = Decimal(str(request.data.get('quantity')))
            from_uom_id = request.data.get('from_uom_id')
            to_uom_id = request.data.get('to_uom_id')
            product_id = request.data.get('product_id')
            
            # Validate inputs
            if not all([quantity, from_uom_id, to_uom_id]):
                return Response(
                    {'error': 'quantity, from_uom_id, and to_uom_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get UoM objects
            try:
                from_uom = UnitOfMeasure.objects.get(id=from_uom_id)
                to_uom = UnitOfMeasure.objects.get(id=to_uom_id)
            except UnitOfMeasure.DoesNotExist:
                return Response(
                    {'error': 'Invalid UoM ID'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get product if provided
            product = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'Invalid product ID'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Perform conversion
            result = UoMConversionService.convert(
                quantity=quantity,
                from_uom=from_uom,
                to_uom=to_uom,
                product=product
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_convert(self, request):
        """
        Perform multiple conversions in bulk
        
        POST /api/products/uom-conversions/bulk_convert/
        Body: {
            "conversions": [
                {"quantity": "10", "from_uom_id": 1, "to_uom_id": 2, "product_id": 5},
                {"quantity": "5", "from_uom_id": 3, "to_uom_id": 4}
            ]
        }
        """
        try:
            conversions = request.data.get('conversions', [])
            
            if not conversions:
                return Response(
                    {'error': 'conversions array is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = UoMConversionService.bulk_convert(conversions)
            
            return Response({
                'results': results,
                'total': len(results),
                'successful': sum(1 for r in results if r.get('success')),
                'failed': sum(1 for r in results if not r.get('success'))
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Bulk conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available_conversions(self, request):
        """
        Get all available conversions from a given UoM
        
        GET /api/products/uom-conversions/available_conversions/?from_uom_id=1
        """
        from_uom_id = request.query_params.get('from_uom_id')
        
        if not from_uom_id:
            return Response(
                {'error': 'from_uom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from_uom = UnitOfMeasure.objects.get(id=from_uom_id)
            conversions = UoMConversionService.get_available_conversions(from_uom)
            
            serializer = self.get_serializer(conversions, many=True)
            
            return Response({
                'from_uom': UnitOfMeasureSerializer(from_uom).data,
                'available_conversions': serializer.data,
                'count': len(conversions)
            }, status=status.HTTP_200_OK)
        
        except UnitOfMeasure.DoesNotExist:
            return Response(
                {'error': 'Invalid UoM ID'},
                status=status.HTTP_404_NOT_FOUND
            )


class UnitOfMeasureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for UnitOfMeasure (read-only)
    """
    queryset = UnitOfMeasure.objects.filter(is_active=True)
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['uom_type', 'is_active']
    search_fields = ['name', 'symbol']


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductVariant CRUD operations
    Task 1.6.2: AJAX Variant Creation
    """
    queryset = ProductVariant.objects.select_related('product').filter(is_active=True)
    serializer_class = ProductVariantQuickCreateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'is_active']
    search_fields = ['variant_name', 'variant_code', 'barcode']
    ordering_fields = ['variant_name', 'variant_code', 'price_adjustment']
    ordering = ['variant_name']
    
    @action(detail=False, methods=['post'], url_path='quick-create')
    def quick_create(self, request):
        """
        Quick-create a product variant from voucher/invoice forms
        
        POST /api/products/variants/quick-create/
        Body: {
            "product": 1,
            "variant_name": "Size: Large",
            "variant_code": "PROD-001-L",
            "price_adjustment": "10.50",  // optional, defaults to 0
            "barcode": "1234567890"       // optional
        }
        
        Returns:
            201: Variant created successfully
            400: Validation error (duplicate code, missing fields, etc.)
            401: Unauthorized
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            variant = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
