"""
ViewSet for Auto-Numbering System API
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from accounting.models import NumberingScheme, Entity
from accounting.serializers.numbering_serializers import (
    NumberingSchemeSerializer,
    GenerateNumberSerializer,
    PreviewNumberSerializer,
    ResetCounterSerializer
)
from accounting.services import NumberingService


class NumberingSchemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing numbering schemes
    
    Provides CRUD operations plus custom actions:
    - generate: Generate next number
    - preview: Preview next number
    - reset: Reset counter
    - scheme_info: Get scheme information
    """
    
    queryset = NumberingScheme.objects.all()
    serializer_class = NumberingSchemeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['document_type', 'is_active', 'entity', 'reset_frequency']
    search_fields = ['scheme_name', 'prefix', 'suffix']
    ordering_fields = ['document_type', 'scheme_name', 'created_at']
    ordering = ['document_type', 'scheme_name']
    
    def perform_create(self, serializer):
        """Set created_by on creation"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate_number(self, request):
        """
        Generate next number for a document type
        
        POST /api/accounting/numbering-schemes/generate/
        Body: {
            "document_type": "invoice",
            "entity_id": 1,  // optional
            "custom_date": "2025-01-29"  // optional
        }
        """
        serializer = GenerateNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document_type = serializer.validated_data['document_type']
        entity_id = serializer.validated_data.get('entity_id')
        custom_date = serializer.validated_data.get('custom_date')
        
        # Get entity if provided
        entity = None
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                return Response(
                    {'error': 'Entity not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Generate number
        try:
            number = NumberingService.generate_number(
                document_type=document_type,
                entity=entity,
                custom_date=custom_date
            )
            
            return Response({
                'number': number,
                'document_type': document_type,
                'entity_id': entity_id,
                'generated_at': custom_date or None
            })
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='preview')
    def preview_number(self, request):
        """
        Preview next number without generating
        
        POST /api/accounting/numbering-schemes/preview/
        Body: {
            "document_type": "invoice",
            "entity_id": 1  // optional
        }
        """
        serializer = PreviewNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document_type = serializer.validated_data['document_type']
        entity_id = serializer.validated_data.get('entity_id')
        
        # Get entity if provided
        entity = None
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                return Response(
                    {'error': 'Entity not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Preview number
        preview = NumberingService.preview_next_number(
            document_type=document_type,
            entity=entity
        )
        
        if preview is None:
            return Response(
                {'error': f'No active numbering scheme found for document type: {document_type}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'preview': preview,
            'document_type': document_type,
            'entity_id': entity_id
        })
    
    @action(detail=True, methods=['post'], url_path='reset')
    def reset_counter(self, request, pk=None):
        """
        Reset counter for a specific scheme
        
        POST /api/accounting/numbering-schemes/{id}/reset/
        Body: {
            "reset_to": 1  // optional, defaults to 1
        }
        """
        scheme = self.get_object()
        
        serializer = ResetCounterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_to = serializer.validated_data.get('reset_to', 1)
        
        # Reset counter
        from datetime import date
        scheme.next_number = reset_to
        scheme.last_reset_date = date.today()
        scheme.save()
        
        return Response({
            'message': f'Counter reset to {reset_to}',
            'scheme_id': scheme.id,
            'scheme_name': scheme.scheme_name,
            'next_number': scheme.next_number,
            'last_reset_date': scheme.last_reset_date
        })
    
    @action(detail=False, methods=['get'], url_path='info')
    def scheme_info(self, request):
        """
        Get scheme information for a document type
        
        GET /api/accounting/numbering-schemes/info/?document_type=invoice&entity_id=1
        """
        document_type = request.query_params.get('document_type')
        entity_id = request.query_params.get('entity_id')
        
        if not document_type:
            return Response(
                {'error': 'document_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get entity if provided
        entity = None
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                return Response(
                    {'error': 'Entity not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get scheme info
        info = NumberingService.get_scheme_info(
            document_type=document_type,
            entity=entity
        )
        
        if info is None:
            return Response(
                {'error': f'No active numbering scheme found for document type: {document_type}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(info)
