from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (WorkCenter, BillOfMaterials, BOMItem, BOMOperation,
                     ProductionOrder, MaterialConsumption, QualityCheck, ProductionDowntime)
from .serializers import (WorkCenterSerializer, BillOfMaterialsSerializer, BOMListSerializer,
                          BOMItemSerializer, BOMOperationSerializer,
                          ProductionOrderSerializer, ProductionOrderListSerializer,
                          MaterialConsumptionSerializer, QualityCheckSerializer,
                          ProductionDowntimeSerializer)

class WorkCenterViewSet(viewsets.ModelViewSet):
    queryset = WorkCenter.objects.all()
    serializer_class = WorkCenterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']

class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.select_related('product', 'uom').prefetch_related('items', 'operations').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'is_active', 'is_default', 'bom_type']
    search_fields = ['product__name', 'product__code', 'version']
    ordering_fields = ['product', 'version', 'created_at']
    ordering = ['-is_default', 'product']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BOMListSerializer
        return BillOfMaterialsSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this BOM as default for the product"""
        bom = self.get_object()
        # Unset other default BOMs for this product
        BillOfMaterials.objects.filter(product=bom.product, is_default=True).update(is_default=False)
        bom.is_default = True
        bom.save()
        serializer = self.get_serializer(bom)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cost_breakdown(self, request, pk=None):
        """Get detailed cost breakdown"""
        bom = self.get_object()
        material_cost = sum(item.total_cost for item in bom.items.all())
        labor_cost = sum(op.operation_cost for op in bom.operations.all())
        
        return Response({
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'total_cost': material_cost + labor_cost,
            'cost_per_unit': (material_cost + labor_cost) / float(bom.quantity) if bom.quantity > 0 else 0
        })

class BOMItemViewSet(viewsets.ModelViewSet):
    queryset = BOMItem.objects.select_related('bom', 'product', 'uom').all()
    serializer_class = BOMItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bom', 'item_type']

class BOMOperationViewSet(viewsets.ModelViewSet):
    queryset = BOMOperation.objects.select_related('bom', 'work_center').all()
    serializer_class = BOMOperationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bom', 'work_center']

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.select_related('product', 'bom', 'uom').prefetch_related(
        'material_consumptions', 'quality_checks', 'downtimes').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'product', 'priority']
    search_fields = ['order_number', 'product__name', 'batch_number', 'lot_number']
    ordering_fields = ['order_number', 'planned_start_date', 'priority', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductionOrderListSerializer
        return ProductionOrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """Start production"""
        order = self.get_object()
        if order.status == 'released':
            order.status = 'in_progress'
            order.actual_start_date = timezone.now()
            order.save()
            return Response({'message': 'Production started'})
        return Response({'error': 'Order must be in released status'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """Complete production"""
        order = self.get_object()
        if order.status == 'in_progress':
            order.status = 'completed'
            order.actual_end_date = timezone.now()
            order.save()
            return Response({'message': 'Production completed'})
        return Response({'error': 'Order must be in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def record_production(self, request, pk=None):
        """Record production quantity"""
        order = self.get_object()
        quantity = request.data.get('quantity', 0)
        rejected = request.data.get('rejected_quantity', 0)
        
        order.produced_quantity += float(quantity)
        order.rejected_quantity += float(rejected)
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Get all in-progress orders"""
        orders = self.queryset.filter(status='in_progress')
        serializer = ProductionOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def planned(self, request):
        """Get all planned orders"""
        orders = self.queryset.filter(status__in=['draft', 'planned', 'released'])
        serializer = ProductionOrderListSerializer(orders, many=True)
        return Response(serializer.data)

class MaterialConsumptionViewSet(viewsets.ModelViewSet):
    queryset = MaterialConsumption.objects.select_related('production_order', 'product', 'uom').all()
    serializer_class = MaterialConsumptionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['production_order']
    
    def perform_create(self, serializer):
        serializer.save(consumed_by=self.request.user)

class QualityCheckViewSet(viewsets.ModelViewSet):
    queryset = QualityCheck.objects.select_related('production_order').all()
    serializer_class = QualityCheckSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['production_order', 'status']
    
    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user)

class ProductionDowntimeViewSet(viewsets.ModelViewSet):
    queryset = ProductionDowntime.objects.select_related('production_order', 'work_center').all()
    serializer_class = ProductionDowntimeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['production_order', 'work_center', 'downtime_type']
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
