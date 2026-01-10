"""
Approval Service
Module 1.3.2: Create ApprovalService

Service for managing approval workflows with IFRS IAS 1 compliance.

Features:
- Initiate approval workflows based on document type and amount
- Approve/reject/delegate approval requests
- Multi-level approval routing
- Amount-based workflow selection
- Complete audit trail
- Segregation of duties enforcement
- Email notifications (placeholder for future implementation)

IFRS Compliance:
- IAS 1: Internal Controls and Governance
- Complete audit trail with non-repudiation
- Immutable approval actions
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from typing import Dict, List, Optional
from accounting.models import (
    ApprovalWorkflow,
    ApprovalLevel,
    ApprovalRequest,
    ApprovalAction,
)


class ApprovalService:
    """
    Service for managing approval workflows
    
    Methods:
    - initiate_approval(): Start approval process for a document
    - approve(): Approve a pending request
    - reject(): Reject a pending request
    - delegate(): Delegate approval to another user
    - get_pending_approvals(): Get all pending approvals for a user
    """
    
    @transaction.atomic
    def initiate_approval(
        self,
        document_type: str,
        document_id: int,
        amount: Decimal,
        requester
    ) -> ApprovalRequest:
        """
        Initiate approval workflow for a document
        
        Args:
            document_type: Type of document (voucher, purchase_order, etc.)
            document_id: ID of the document
            amount: Amount of the document
            requester: User who is requesting approval
            
        Returns:
            ApprovalRequest object
            
        Raises:
            ValidationError: If no workflow exists or duplicate request
        """
        # Find active workflow for document type
        try:
            workflow = ApprovalWorkflow.objects.get(
                document_type=document_type,
                is_active=True
            )
        except ApprovalWorkflow.DoesNotExist:
            raise ValidationError(
                f"No active approval workflow found for document type: {document_type}"
            )
        
        # Check for duplicate approval request
        existing = ApprovalRequest.objects.filter(
            document_type=document_type,
            document_id=document_id,
            status__in=['pending', 'approved']
        ).exists()
        
        if existing:
            raise ValidationError(
                f"Approval request already exists for {document_type} #{document_id}"
            )
        
        # Determine first approval level based on amount
        first_level = self._get_first_approval_level(workflow, amount)
        
        if not first_level:
            raise ValidationError(
                f"No approval level found for amount {amount} in workflow {workflow.workflow_name}"
            )
        
        # Create approval request
        approval_request = ApprovalRequest.objects.create(
            workflow=workflow,
            document_type=document_type,
            document_id=document_id,
            amount=amount,
            current_level=first_level.level_number,
            status='pending',
            requester=requester,
            current_approver=first_level.approver
        )
        
        # TODO: Send email notification to first approver
        # self._send_notification(first_level.approver, approval_request, 'new_request')
        
        return approval_request
    
    @transaction.atomic
    def approve(
        self,
        approval_request_id: int,
        approver,
        comments: str = '',
        ip_address: str = '0.0.0.0'
    ) -> Dict:
        """
        Approve a pending approval request
        
        Args:
            approval_request_id: ID of the approval request
            approver: User who is approving
            comments: Optional comments
            ip_address: IP address of approver
            
        Returns:
            Dict with approval status and next steps
            
        Raises:
            ValidationError: If request not found, wrong approver, or already processed
        """
        # Get approval request
        try:
            approval_request = ApprovalRequest.objects.select_for_update().get(
                id=approval_request_id
            )
        except ApprovalRequest.DoesNotExist:
            raise ValidationError(f"Approval request #{approval_request_id} not found")
        
        # Validate request status
        if approval_request.status != 'pending':
            raise ValidationError(
                f"Approval request is already {approval_request.status}"
            )
        
        # Validate approver
        if approval_request.current_approver != approver:
            raise ValidationError(
                f"You are not the assigned approver for this request. "
                f"Current approver: {approval_request.current_approver.username}"
            )
        
        # Enforce segregation of duties (IAS 1 - Internal Controls)
        if approval_request.requester == approver:
            raise ValidationError(
                "Segregation of duties violation: Requester cannot approve their own request (IAS 1)"
            )
        
        # Record approval action
        ApprovalAction.objects.create(
            approval_request=approval_request,
            level_number=approval_request.current_level,
            approver=approver,
            action='approved',
            comments=comments,
            ip_address=ip_address
        )
        
        
        current_level_number_before_update = approval_request.current_level
        
        # Check if there are more levels
        next_level = self._get_next_approval_level(
            approval_request.workflow,
            approval_request.amount,
            approval_request.current_level
        )
        
        if next_level:
            # Move to next level
            approval_request.current_level = next_level.level_number
            approval_request.current_approver = next_level.approver
            approval_request.save()
            
            # TODO: Send notification to next approver
            # self._send_notification(next_level.approver, approval_request, 'pending_approval')
            
            return {
                'approved': False,
                'status': 'pending',
                'next_level': next_level.level_number,
                'next_approver_id': next_level.approver.id,
                'next_approver_username': next_level.approver.username,
                'message': f'Approved at level {current_level_number_before_update}. Moved to level {next_level.level_number}.'
            }
        else:
            # Final approval - complete the request
            approval_request.status = 'approved'
            approval_request.completion_date = timezone.now()
            approval_request.save()
            
            # TODO: Send notification to requester
            # self._send_notification(approval_request.requester, approval_request, 'approved')
            
            return {
                'approved': True,
                'status': 'approved',
                'message': 'Approval request fully approved'
            }
    
    @transaction.atomic
    def reject(
        self,
        approval_request_id: int,
        approver,
        comments: str = '',
        ip_address: str = '0.0.0.0'
    ) -> Dict:
        """
        Reject a pending approval request
        
        Args:
            approval_request_id: ID of the approval request
            approver: User who is rejecting
            comments: Reason for rejection
            ip_address: IP address of approver
            
        Returns:
            Dict with rejection status
            
        Raises:
            ValidationError: If request not found, wrong approver, or already processed
        """
        # Get approval request
        try:
            approval_request = ApprovalRequest.objects.select_for_update().get(
                id=approval_request_id
            )
        except ApprovalRequest.DoesNotExist:
            raise ValidationError(f"Approval request #{approval_request_id} not found")
        
        # Validate request status
        if approval_request.status != 'pending':
            raise ValidationError(
                f"Approval request is already {approval_request.status}"
            )
        
        # Validate approver
        if approval_request.current_approver != approver:
            raise ValidationError(
                f"You are not the assigned approver for this request. "
                f"Current approver: {approval_request.current_approver.username}"
            )
        
        # Record rejection action
        ApprovalAction.objects.create(
            approval_request=approval_request,
            level_number=approval_request.current_level,
            approver=approver,
            action='rejected',
            comments=comments,
            ip_address=ip_address
        )
        
        # Mark request as rejected
        approval_request.status = 'rejected'
        approval_request.completion_date = timezone.now()
        approval_request.save()
        
        # TODO: Send notification to requester
        # self._send_notification(approval_request.requester, approval_request, 'rejected')
        
        return {
            'rejected': True,
            'status': approval_request.status,
            'message': f'Rejected at level {approval_request.current_level}'
        }
    
    @transaction.atomic
    def delegate(
        self,
        approval_request_id: int,
        approver,
        delegate_to,
        comments: str = '',
        ip_address: str = '0.0.0.0'
    ) -> Dict:
        """
        Delegate approval to another user
        
        Args:
            approval_request_id: ID of the approval request
            approver: Current approver who is delegating
            delegate_to: User to delegate to
            comments: Reason for delegation
            ip_address: IP address of approver
            
        Returns:
            Dict with delegation status
            
        Raises:
            ValidationError: If request not found, wrong approver, or delegating to self
        """
        # Get approval request
        try:
            approval_request = ApprovalRequest.objects.select_for_update().get(
                id=approval_request_id
            )
        except ApprovalRequest.DoesNotExist:
            raise ValidationError(f"Approval request #{approval_request_id} not found")
        
        # Validate request status
        if approval_request.status != 'pending':
            raise ValidationError(
                f"Approval request is already {approval_request.status}"
            )
        
        # Validate approver
        if approval_request.current_approver != approver:
            raise ValidationError(
                f"You are not the assigned approver for this request. "
                f"Current approver: {approval_request.current_approver.username}"
            )
        
        # Validate delegation target
        if approver == delegate_to:
            raise ValidationError("Cannot delegate to yourself")
        
        # Record delegation action
        ApprovalAction.objects.create(
            approval_request=approval_request,
            level_number=approval_request.current_level,
            approver=approver,
            action='delegated',
            comments=f"Delegated to {delegate_to.username}. {comments}",
            ip_address=ip_address
        )
        
        # Update current approver
        approval_request.current_approver = delegate_to
        approval_request.save()
        
        # TODO: Send notification to delegate
        # self._send_notification(delegate_to, approval_request, 'delegated')
        
        return {
            'delegated': True,
            'new_approver_id': delegate_to.id,
            'new_approver_username': delegate_to.username,
            'message': f'Approval delegated to {delegate_to.username}'
        }
    
    def get_pending_approvals(self, approver) -> List[ApprovalRequest]:
        """
        Get all pending approval requests for a user
        
        Args:
            approver: User to get pending approvals for
            
        Returns:
            List of ApprovalRequest objects
        """
        return list(
            ApprovalRequest.objects.filter(
                current_approver=approver,
                status='pending'
            ).select_related(
                'workflow',
                'requester',
                'current_approver'
            ).order_by('-request_date')
        )
    
    def _get_first_approval_level(
        self,
        workflow: ApprovalWorkflow,
        amount: Decimal
    ) -> Optional[ApprovalLevel]:
        """
        Get the first approval level for a workflow
        
        Always returns level 1 if it exists. Multi-level workflows
        should start at level 1 and progress through levels.
        
        Args:
            workflow: ApprovalWorkflow object
            amount: Amount to check (not used for first level selection)
            
        Returns:
            ApprovalLevel object or None
        """
        # Always start at level 1
        return ApprovalLevel.objects.filter(
            workflow=workflow,
            level_number=1,
            is_mandatory=True
        ).first()
    
    def _get_next_approval_level(
        self,
        workflow: ApprovalWorkflow,
        amount: Decimal,
        current_level: int
    ) -> Optional[ApprovalLevel]:
        """
        Get the next approval level for a workflow
        
        Args:
            workflow: ApprovalWorkflow object
            amount: Amount to check
            current_level: Current level number
            
        Returns:
            ApprovalLevel object or None
        """
        # Get next level that matches amount range
        next_levels = ApprovalLevel.objects.filter(
            workflow=workflow,
            level_number__gt=current_level,
            min_amount__lte=amount,
            max_amount__gte=amount,
            is_mandatory=True
        ).order_by('level_number')
        
        return next_levels.first()
    
    def _send_notification(self, user, approval_request: ApprovalRequest, notification_type: str):
        """
        Send email notification (placeholder for future implementation)
        
        Args:
            user: User to notify
            approval_request: ApprovalRequest object
            notification_type: Type of notification (new_request, pending_approval, approved, rejected, delegated)
        """
        # TODO: Implement email notification
        # This will be implemented in Task 1.3.2 when email system is ready
        pass
    
    @transaction.atomic
    def initiate_approval_for_voucher(self, voucher) -> ApprovalRequest:
        """
        Initiate approval workflow for a VoucherV2 instance
        
        Task 1.3.4: Integration with Existing Models
        IAS 1 - Internal Controls: Initiate approval for vouchers
        
        Args:
            voucher: VoucherV2 instance
            
        Returns:
            ApprovalRequest object
            
        Raises:
            ValidationError: If no workflow exists or validation fails
        """
        # Use the generic initiate_approval method
        approval_request = self.initiate_approval(
            document_type='voucher',
            document_id=voucher.id,
            amount=voucher.total_amount,
            requester=voucher.created_by
        )
        
        # Link voucher to approval request and set status
        voucher.approval_status = 'pending'
        voucher.approval_request = approval_request
        voucher.save(update_fields=['approval_status', 'approval_request'])
        
        return approval_request
