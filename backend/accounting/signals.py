"""
Django Signal Handlers for Audit Logging
Task 1.7.2: Django Signals Integration
Module 1.7: Audit Trail System (IASB Requirement)

Automatically logs all data changes via Django signals
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from threading import local
from accounting.models import AccountV2, AuditLog
from accounting.services.audit_service import AuditService

User = get_user_model()

# Thread-local storage for audit context
_audit_context = local()


def set_audit_context(user, ip_address, reason=''):
    """
    Set audit context for the current thread
    
    Call this in views/APIs before making model changes:
        set_audit_context(request.user, AuditService.get_client_ip(request))
    
    Args:
        user (User): User performing the action
        ip_address (str): IP address of the user
        reason (str, optional): Reason for the change
    """
    _audit_context.user = user
    _audit_context.ip_address = ip_address
    _audit_context.reason = reason


def get_audit_context():
    """
    Get audit context for the current thread
    
    Returns:
        dict: Dictionary with user, ip_address, and reason
    """
    return {
        'user': getattr(_audit_context, 'user', None),
        'ip_address': getattr(_audit_context, 'ip_address', '127.0.0.1'),
        'reason': getattr(_audit_context, 'reason', '')
    }


def clear_audit_context():
    """Clear audit context for the current thread"""
    if hasattr(_audit_context, 'user'):
        del _audit_context.user
    if hasattr(_audit_context, 'ip_address'):
        del _audit_context.ip_address
    if hasattr(_audit_context, 'reason'):
        del _audit_context.reason


# Store original data before save for UPDATE detection
_original_data = {}


@receiver(pre_save)
def store_original_data(sender, instance, **kwargs):
    """
    Store original data before save for UPDATE detection
    
    This signal fires before save() to capture the original state
    """
    # Skip for AuditLog itself to avoid recursion
    if sender == AuditLog:
        return
    
    # Only store if object already exists (UPDATE case)
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            _original_data[instance.pk] = {}
            
            for field in instance._meta.fields:
                field_name = field.name
                _original_data[instance.pk][field_name] = getattr(original, field_name, None)
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Log model creation and updates
    
    This signal fires after save() to log the change
    
    Args:
        sender: Model class
        instance: Model instance that was saved
        created (bool): True if this is a new object
        **kwargs: Additional keyword arguments
    """
    # Skip for AuditLog itself to avoid recursion
    if sender == AuditLog:
        return
    
    # Skip if no audit context (e.g., migrations, management commands)
    context = get_audit_context()
    if not context['user']:
        return
    
    # Determine action
    action = 'CREATE' if created else 'UPDATE'
    
    # Get changes
    if created:
        changes = AuditService.get_model_changes(instance, is_creation=True)
    else:
        original_data = _original_data.get(instance.pk, {})
        changes = AuditService.get_model_changes(
            instance,
            is_creation=False,
            original_data=original_data
        )
        
        # Clean up stored data
        if instance.pk in _original_data:
            del _original_data[instance.pk]
    
    # Log the change
    try:
        AuditService.log_change(
            model_name=sender.__name__,
            object_id=instance.pk,
            action=action,
            user=context['user'],
            ip_address=context['ip_address'],
            changes=changes,
            reason=context['reason']
        )
    except Exception as e:
        # Log error but don't break the transaction
        print(f"Audit logging error: {e}")


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """
    Log model deletions
    
    This signal fires after delete() to log the deletion
    
    Args:
        sender: Model class
        instance: Model instance that was deleted
        **kwargs: Additional keyword arguments
    """
    # Skip for AuditLog itself to avoid recursion
    if sender == AuditLog:
        return
    
    # Skip if no audit context
    context = get_audit_context()
    if not context['user']:
        return
    
    # Capture deleted object data
    changes = {
        'deleted_object': {}
    }
    
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name, None)
        if field_value is not None:
            changes['deleted_object'][field_name] = str(field_value)
    
    # Log the deletion
    try:
        AuditService.log_change(
            model_name=sender.__name__,
            object_id=instance.pk,
            action='DELETE',
            user=context['user'],
            ip_address=context['ip_address'],
            changes=changes,
            reason=context['reason']
        )
    except Exception as e:
        # Log error but don't break the transaction
        print(f"Audit logging error: {e}")


# Register signals for specific models (optional - can be done in apps.py)
def register_audit_signals():
    """
    Register audit signals for critical models
    
    Call this in apps.py ready() method
    """
    # Signals are already registered via @receiver decorator
    # This function is here for explicit registration if needed
    pass
