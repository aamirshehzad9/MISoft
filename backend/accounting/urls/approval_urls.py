"""
URL Configuration for Approval Workflow API
Module 1.3.3: Create Approval API & UI

Registers the following endpoints:
- /api/approval-workflows/
- /api/approval-levels/
- /api/approval-requests/
- /api/approval-actions/

Custom actions:
- POST /api/approval-requests/{id}/approve/
- POST /api/approval-requests/{id}/reject/
- POST /api/approval-requests/{id}/delegate/
- GET /api/approval-requests/pending_approvals/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounting.views.approval_views import (
    ApprovalWorkflowViewSet,
    ApprovalLevelViewSet,
    ApprovalRequestViewSet,
    ApprovalActionViewSet,
)

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'approval-workflows', ApprovalWorkflowViewSet, basename='approvalworkflow')
router.register(r'approval-levels', ApprovalLevelViewSet, basename='approvallevel')
router.register(r'approval-requests', ApprovalRequestViewSet, basename='approvalrequest')
router.register(r'approval-actions', ApprovalActionViewSet, basename='approvalaction')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
