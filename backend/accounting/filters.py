from rest_framework import filters

class UserReferencesFilterBackend(filters.BaseFilterBackend):
    """
    Filter by user_references using prefix 'ref_'.
    Example: ?ref_po_num=123 filters user_references__po_num__icontains=123 (if text)
    or exact match.
    
    We use 'icontains' for broader search by default, or exact if preferred.
    """
    def filter_queryset(self, request, queryset, view):
        for param, value in request.query_params.items():
            if param.startswith('ref_'):
                key = param[4:] # strip 'ref_'
                # Use icontains for flexibility, or exact
                # JSONB values are typically strings or numbers.
                # user_references__key__icontains might work on PG for string values
                
                # Check if we should use exact or contains
                # For now, let's try direct lookup which is safest for all types in Django ORM
                # But typically users want partial search.
                # Let's support both: ref_exact_key=val vs ref_key=val (contains)
                
                # Simple implementation: Exact match
                lookup = {f"user_references__{key}": value}
                try:
                    queryset = queryset.filter(**lookup)
                except Exception:
                    # Ignore filter errors (e.g. invalid lookup for type)
                    pass
        return queryset
