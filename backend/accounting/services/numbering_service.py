"""
Numbering Service for Auto-Numbering System

Provides thread-safe number generation for all document types.

Features:
- Thread-safe number generation using database locks
- Automatic reset based on frequency
- Multi-entity support
- Fallback to default scheme if entity-specific not found
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from typing import Optional

from accounting.models import NumberingScheme, Entity


class NumberingService:
    """
    Service for generating sequential document numbers
    
    Thread-safe implementation using database-level locking
    to prevent duplicate numbers in concurrent environments.
    """
    
    @staticmethod
    @transaction.atomic
    def generate_number(
        document_type: str,
        entity: Optional[Entity] = None,
        custom_date: Optional[date] = None
    ) -> str:
        """
        Generate next sequential number for a document type
        
        Args:
            document_type: Type of document (invoice, voucher, etc.)
            entity: Specific entity (optional, uses global scheme if None)
            custom_date: Custom date for number generation (defaults to today)
            
        Returns:
            Generated document number (e.g., "INV-2025-0001")
            
        Raises:
            ValidationError: If no active scheme found for document type
        """
        # Get the active numbering scheme
        scheme = NumberingService._get_active_scheme(document_type, entity)
        
        if not scheme:
            raise ValidationError(
                f"No active numbering scheme found for document type: {document_type}"
            )
        
        # Use select_for_update to lock the row for thread safety
        scheme = NumberingScheme.objects.select_for_update().get(pk=scheme.pk)
        
        # Check if counter should be reset
        if scheme.should_reset(compare_date=custom_date):
            scheme.next_number = 1
            scheme.last_reset_date = custom_date or date.today()
        
        # Generate the number
        number = NumberingService._format_number(scheme, custom_date)
        
        # Increment counter
        scheme.next_number += 1
        scheme.save()
        
        return number
    
    @staticmethod
    def _get_active_scheme(
        document_type: str,
        entity: Optional[Entity] = None
    ) -> Optional[NumberingScheme]:
        """
        Get active numbering scheme for document type
        
        Priority:
        1. Entity-specific active scheme
        2. Global active scheme
        """
        # Try entity-specific scheme first
        if entity:
            scheme = NumberingScheme.objects.filter(
                document_type=document_type,
                entity=entity,
                is_active=True
            ).first()
            
            if scheme:
                return scheme
        
        # Fall back to global scheme
        return NumberingScheme.objects.filter(
            document_type=document_type,
            entity__isnull=True,
            is_active=True
        ).first()
    
    @staticmethod
    def _format_number(
        scheme: NumberingScheme,
        custom_date: Optional[date] = None
    ) -> str:
        """
        Format the number according to scheme configuration
        
        Args:
            scheme: NumberingScheme instance
            custom_date: Custom date for formatting (defaults to today)
            
        Returns:
            Formatted number string
        """
        components = []
        use_date = custom_date or date.today()
        
        # Add prefix
        if scheme.prefix:
            components.append(scheme.prefix)
        
        # Add date component
        if scheme.date_format:
            if scheme.date_format == 'YYYY':
                components.append(str(use_date.year))
            elif scheme.date_format == 'YY':
                components.append(str(use_date.year)[2:])
            elif scheme.date_format == 'YYMM':
                components.append(f"{str(use_date.year)[2:]}{use_date.month:02d}")
            elif scheme.date_format == 'YYYYMM':
                components.append(f"{use_date.year}{use_date.month:02d}")
            elif scheme.date_format == 'YYMMDD':
                components.append(f"{str(use_date.year)[2:]}{use_date.month:02d}{use_date.day:02d}")
            elif scheme.date_format == 'YYYYMMDD':
                components.append(f"{use_date.year}{use_date.month:02d}{use_date.day:02d}")
        
        # Add sequence number (current next_number before increment)
        sequence = str(scheme.next_number).zfill(scheme.padding)
        components.append(sequence)
        
        # Add suffix
        if scheme.suffix:
            components.append(scheme.suffix)
        
        # Join with separator
        return scheme.separator.join(components)
    
    @staticmethod
    def preview_next_number(
        document_type: str,
        entity: Optional[Entity] = None
    ) -> Optional[str]:
        """
        Preview what the next number will be without generating it
        
        Args:
            document_type: Type of document
            entity: Specific entity (optional)
            
        Returns:
            Preview of next number, or None if no scheme found
        """
        scheme = NumberingService._get_active_scheme(document_type, entity)
        
        if not scheme:
            return None
        
        return scheme.generate_preview()
    
    @staticmethod
    def reset_counter(
        document_type: str,
        entity: Optional[Entity] = None,
        reset_to: int = 1
    ) -> bool:
        """
        Manually reset counter for a numbering scheme
        
        Args:
            document_type: Type of document
            entity: Specific entity (optional)
            reset_to: Number to reset to (default: 1)
            
        Returns:
            True if reset successful, False if scheme not found
        """
        scheme = NumberingService._get_active_scheme(document_type, entity)
        
        if not scheme:
            return False
        
        scheme.next_number = reset_to
        scheme.last_reset_date = date.today()
        scheme.save()
        
        return True
    
    @staticmethod
    def get_scheme_info(
        document_type: str,
        entity: Optional[Entity] = None
    ) -> Optional[dict]:
        """
        Get information about active numbering scheme
        
        Args:
            document_type: Type of document
            entity: Specific entity (optional)
            
        Returns:
            Dict with scheme information, or None if not found
        """
        scheme = NumberingService._get_active_scheme(document_type, entity)
        
        if not scheme:
            return None
        
        return {
            'scheme_name': scheme.scheme_name,
            'document_type': scheme.document_type,
            'format_preview': scheme.generate_preview(),
            'next_number': scheme.next_number,
            'reset_frequency': scheme.reset_frequency,
            'last_reset_date': scheme.last_reset_date,
            'entity': scheme.entity.entity_code if scheme.entity else None,
        }
