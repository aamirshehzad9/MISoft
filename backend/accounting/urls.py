"""
URL Configuration for Accounting App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounting.views import (
    AuditLogViewSet, BankStatementViewSet, BankReconciliationViewSet,
    ChequeViewSet, BankTransferViewSet, InvoiceViewSet, VoucherV2ViewSet,
    AccountV2ViewSet, AssetCategoryViewSet, FixedAssetViewSet,
    FiscalYearViewSet, TaxCodeViewSet, TaxMasterV2ViewSet, TaxGroupV2ViewSet,
    CurrencyV2ViewSet, ExchangeRateV2ViewSet, CostCenterV2ViewSet, DepartmentV2ViewSet, EntityV2ViewSet,
    BankAccountViewSet, FairValueMeasurementViewSet, FXRevaluationLogViewSet,
    fixed_asset_register_report, assets_by_category_report, assets_by_location_report
)

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')
router.register(r'bank-statements', BankStatementViewSet, basename='bank-statements')
router.register(r'bank-reconciliations', BankReconciliationViewSet, basename='bank-reconciliations')
router.register(r'cheques', ChequeViewSet, basename='cheque')
router.register(r'bank-transfers', BankTransferViewSet, basename='bank-transfer')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'vouchers-v2', VoucherV2ViewSet, basename='voucher-v2')
router.register(r'accounts-v2', AccountV2ViewSet, basename='account-v2')
router.register(r'asset-categories', AssetCategoryViewSet, basename='asset-category')
router.register(r'fixed-assets', FixedAssetViewSet, basename='fixed-asset')
router.register(r'fiscal-years', FiscalYearViewSet, basename='fiscal-year')
router.register(r'tax-codes', TaxCodeViewSet, basename='tax-code')
router.register(r'tax-masters-v2', TaxMasterV2ViewSet, basename='tax-master-v2')
router.register(r'tax-groups-v2', TaxGroupV2ViewSet, basename='tax-group-v2')
router.register(r'currencies-v2', CurrencyV2ViewSet, basename='currency-v2')
router.register(r'exchange-rates-v2', ExchangeRateV2ViewSet, basename='exchange-rate-v2')
router.register(r'cost-centers-v2', CostCenterV2ViewSet, basename='cost-center-v2')
router.register(r'departments-v2', DepartmentV2ViewSet, basename='department-v2')
router.register(r'entities-v2', EntityV2ViewSet, basename='entity-v2')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'fair-value-measurements', FairValueMeasurementViewSet, basename='fair-value-measurement')
router.register(r'fx-revaluation-logs', FXRevaluationLogViewSet, basename='fx-revaluation-log')

urlpatterns = [
    path('', include(router.urls)),
    # Asset Reports
    path('reports/fixed-asset-register/', fixed_asset_register_report, name='fixed-asset-register'),
    path('reports/assets-by-category/', assets_by_category_report, name='assets-by-category'),
    path('reports/assets-by-location/', assets_by_location_report, name='assets-by-location'),
]
