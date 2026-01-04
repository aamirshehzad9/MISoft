import re
from typing import Dict, Any, List
from django.core.exceptions import ValidationError
from datetime import date
from .models import ReferenceDefinition

class ReferenceValidator:
    """
    Validator for User-Defined References (JSONB)
    Enforces rules defined in ReferenceDefinition model.
    """
    
    @staticmethod
    def validate(model_name: str, references: Dict[str, Any], exclude_id: int = None) -> None:
        """
        Validate references against active definitions.
        Raises ValidationError if invalid.
        """
        if not isinstance(references, dict):
             raise ValidationError({"user_references": "References must be a JSON object"})

        definitions = ReferenceDefinition.objects.filter(
            model_name=model_name, 
            is_active=True
        )
        
        errors = {}
        
        # Check definitions against data
        for defn in definitions:
            if defn.is_required and defn.field_key not in references:
                errors[defn.field_key] = f"Field '{defn.field_label}' is required."
                continue
            
            if defn.field_key in references:
                value = references[defn.field_key]
                # Skip empty values if not required? 
                # If required, empty string might be invalid. 
                # For now, validate type if present.
                if value is None and not defn.is_required:
                    continue
                if value is None and defn.is_required:
                    errors[defn.field_key] = "Field cannot be null."
                    continue

                error = ReferenceValidator._validate_field(defn, value)
                if error:
                    errors[defn.field_key] = error
                    continue

                # Check uniqueness if valid type
                if defn.is_unique:
                    unique_error = ReferenceValidator._check_uniqueness(model_name, defn.field_key, value, exclude_id)
                    if unique_error:
                         errors[defn.field_key] = unique_error
        
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _check_uniqueness(model_name: str, key: str, value: Any, exclude_id: int = None) -> str:
        from django.apps import apps
        model_map = {
            'voucher': 'accounting.VoucherV2',
            'invoice': 'accounting.Invoice'
        }
        app_label = model_map.get(model_name)
        if not app_label:
            return None
            
        try:
            Model = apps.get_model(app_label)
            # JsonField lookup: user_references__key = value
            query = {f"user_references__{key}": value}
            qs = Model.objects.filter(**query)
            if exclude_id:
                qs = qs.exclude(id=exclude_id)
                
            if qs.exists():
                return f"Value '{value}' must be unique."
        except Exception:
            # Fallback if model logic fails or lookup invalid
            return None
        return None
    
    @staticmethod
    def _validate_field(defn: ReferenceDefinition, value: Any) -> str:
        """Validate a single field value against definition"""
        
        if defn.data_type == 'text':
            if not isinstance(value, str):
                return "Must be text."
            if defn.validation_regex:
                try:
                    if not re.match(defn.validation_regex, value):
                        return f"Format invalid."
                except re.error:
                    pass # Ignore bad regex for now to avoid crashing app
                    
        elif defn.data_type == 'number':
            if isinstance(value, str):
                try:
                    float(value)
                except ValueError:
                     return "Must be a number."
            elif not isinstance(value, (int, float)):
                 return "Must be a number."
                     
        elif defn.data_type == 'boolean':
             if not isinstance(value, bool):
                 # Allow "true"/"false" strings? Standard JSON usually implies native types.
                 # But let's be strict for cleanliness.
                 return "Must be a boolean (true/false)."
                 
        elif defn.data_type == 'date':
            value_str = str(value)
            try:
                date.fromisoformat(value_str)
            except ValueError:
                return "Invalid date format (use YYYY-MM-DD)."
                
        return None
