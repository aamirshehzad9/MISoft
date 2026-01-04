"""
Audit Service for automatic audit logging
Task 1.7.2: Django Signals Integration
Module 1.7: Audit Trail System (IASB Requirement)

Provides centralized audit logging functionality
"""
from django.contrib.auth import get_user_model
from accounting.models import AuditLog

User = get_user_model()


class AuditService:
    """
    Service class for audit logging
    
    Provides methods to log all data changes for IFRS/IASB compliance
    """
    
    @staticmethod
    def log_change(model_name, object_id, action, user, ip_address, changes, reason=''):
        """
        Log a data change to the audit trail
        
        Args:
            model_name (str): Name of the model that was changed
            object_id (int): ID of the object that was changed
            action (str): Action performed (CREATE, UPDATE, DELETE)
            user (User): User who performed the action
            ip_address (str): IP address of the user
            changes (dict): Dictionary containing the changes
            reason (str, optional): Reason for the change
        
        Returns:
            AuditLog: The created audit log entry
        
        Example:
            AuditService.log_change(
                model_name='AccountV2',
                object_id=123,
                action='UPDATE',
                user=request.user,
                ip_address='192.168.1.1',
                changes={'before': {'balance': '1000'}, 'after': {'balance': '1500'}},
                reason='Monthly adjustment'
            )
        """
        audit = AuditLog.objects.create(
            model_name=model_name,
            object_id=object_id,
            action=action,
            user=user,
            ip_address=ip_address,
            changes=changes,
            reason=reason
        )
        
        return audit
    
    @staticmethod
    def get_client_ip(request):
        """
        Extract client IP address from request
        
        Handles proxied requests by checking X-Forwarded-For header
        
        Args:
            request: Django HTTP request object
        
        Returns:
            str: Client IP address
        """
        # Check for X-Forwarded-For header (proxied requests)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list (client IP)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Direct connection
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        return ip
    
    @staticmethod
    def get_model_changes(instance, is_creation=False, original_data=None):
        """
        Extract changes from a model instance
        
        Args:
            instance: Django model instance
            is_creation (bool): Whether this is a new object creation
            original_data (dict, optional): Original field values for UPDATE
        
        Returns:
            dict: Dictionary containing the changes
        """
        if is_creation:
            # For CREATE, capture all field values
            changes = {}
            for field in instance._meta.fields:
                field_name = field.name
                field_value = getattr(instance, field_name, None)
                
                # Convert to string for JSON serialization
                if field_value is not None:
                    changes[field_name] = str(field_value)
            
            return changes
        else:
            # For UPDATE, capture before/after values
            if original_data is None:
                original_data = {}
            
            changes = {
                'before': {},
                'after': {}
            }
            
            for field in instance._meta.fields:
                field_name = field.name
                new_value = getattr(instance, field_name, None)
                old_value = original_data.get(field_name)
                
                # Only include changed fields
                if str(old_value) != str(new_value):
                    changes['before'][field_name] = str(old_value) if old_value is not None else None
                    changes['after'][field_name] = str(new_value) if new_value is not None else None
            
            return changes
    
    @staticmethod
    def get_audit_history(model_name, object_id):
        """
        Retrieve complete audit history for an object
        
        Args:
            model_name (str): Name of the model
            object_id (int): ID of the object
        
        Returns:
            QuerySet: Audit logs ordered by timestamp (newest first)
        """
        return AuditLog.objects.filter(
            model_name=model_name,
            object_id=object_id
        ).order_by('-timestamp')
    
    @staticmethod
    def get_user_audit_trail(user, start_date=None, end_date=None):
        """
        Retrieve all actions performed by a specific user
        
        Args:
            user (User): User to get audit trail for
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
        
        Returns:
            QuerySet: Audit logs for the user
        """
        queryset = AuditLog.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.order_by('-timestamp')
    
    @staticmethod
    def get_model_audit_trail(model_name, start_date=None, end_date=None):
        """
        Retrieve all changes for a specific model
        
        Args:
            model_name (str): Name of the model
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
        
        Returns:
            QuerySet: Audit logs for the model
        """
        queryset = AuditLog.objects.filter(model_name=model_name)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.order_by('-timestamp')
    
    @staticmethod
    def generate_user_activity_report(user_id=None, start_date=None, end_date=None):
        """
        Generate report of user activities
        
        Args:
            user_id (int, optional): Filter by user ID
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date
            
        Returns:
            dict: Report data with summary and per-user details
        """
        from django.db.models import Count, Q
        
        queryset = AuditLog.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        # Summary statistics
        total_actions = queryset.count()
        total_users = queryset.values('user').distinct().count()
        
        # User breakdown
        user_stats = queryset.values(
            'user__id', 'user__username', 'user__email', 'user__first_name', 'user__last_name'
        ).annotate(
            total_actions=Count('id'),
            creates=Count('id', filter=Q(action='CREATE')),
            updates=Count('id', filter=Q(action='UPDATE')),
            deletes=Count('id', filter=Q(action='DELETE'))
        ).order_by('-total_actions')
        
        users_data = []
        for stat in user_stats:
            users_data.append({
                'user': {
                    'id': stat['user__id'],
                    'username': stat['user__username'],
                    'email': stat['user__email'],
                    'name': f"{stat['user__first_name']} {stat['user__last_name']}".strip()
                },
                'total_actions': stat['total_actions'],
                'actions_breakdown': {
                    'CREATE': stat['creates'],
                    'UPDATE': stat['updates'],
                    'DELETE': stat['deletes']
                }
            })
            
        return {
            'summary': {
                'total_users': total_users,
                'total_actions': total_actions,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            },
            'users': users_data
        }

    @staticmethod
    def generate_change_history_report(model_name=None, start_date=None, end_date=None):
        """
        Generate report of changes by model
        
        Args:
            model_name (str, optional): Filter by model name
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date
            
        Returns:
            dict: Report data with summary and per-model details
        """
        from django.db.models import Count, Q
        
        queryset = AuditLog.objects.all()
        
        if model_name:
            queryset = queryset.filter(model_name__iexact=model_name)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        # Summary statistics
        total_changes = queryset.count()
        total_models = queryset.values('model_name').distinct().count()
        
        # Model breakdown
        model_stats = queryset.values('model_name').annotate(
            total_changes=Count('id'),
            creates=Count('id', filter=Q(action='CREATE')),
            updates=Count('id', filter=Q(action='UPDATE')),
            deletes=Count('id', filter=Q(action='DELETE'))
        ).order_by('-total_changes')
        
        models_data = []
        for stat in model_stats:
            models_data.append({
                'model_name': stat['model_name'],
                'total_changes': stat['total_changes'],
                'actions_breakdown': {
                    'CREATE': stat['creates'],
                    'UPDATE': stat['updates'],
                    'DELETE': stat['deletes']
                }
            })
            
        return {
            'summary': {
                'total_models': total_models,
                'total_changes': total_changes,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            },
            'models': models_data
        }

    @staticmethod
    def generate_object_audit_report(model_name, object_id):
        """
        Generate audit report for a specific object
        
        Args:
            model_name (str): Name of the model
            object_id (int): ID of the object
            
        Returns:
            dict: Report data with summary and history
        """
        if not model_name or not object_id:
            raise ValueError("model_name and object_id are required")
            
        queryset = AuditLog.objects.filter(
            model_name__iexact=model_name,
            object_id=object_id
        ).select_related('user').order_by('-timestamp')
        
        total_changes = queryset.count()
        
        history_data = []
        for log in queryset:
            history_data.append({
                'id': log.id,
                'action': log.action,
                'timestamp': log.timestamp,
                'user': {
                    'id': log.user.id,
                    'username': log.user.username,
                    'name': f"{log.user.first_name} {log.user.last_name}".strip()
                },
                'ip_address': log.ip_address,
                'changes': log.changes,
                'reason': log.reason
            })
            
        return {
            'summary': {
                'model_name': model_name,
                'object_id': object_id,
                'total_changes': total_changes,
                'last_updated': queryset.first().timestamp if total_changes > 0 else None
            },
            'history': history_data
        }
