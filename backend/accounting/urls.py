from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FiscalYearViewSet, AccountTypeViewSet, ChartOfAccountsViewSet,
                    JournalEntryViewSet, InvoiceViewSet, PaymentViewSet,
                    BankAccountViewSet, TaxCodeViewSet, AccountV2ViewSet, VoucherV2ViewSet)

router = DefaultRouter()
router.register(r'fiscal-years', FiscalYearViewSet, basename='fiscalyear')
router.register(r'account-types', AccountTypeViewSet, basename='accounttype')
router.register(r'chart-of-accounts', ChartOfAccountsViewSet, basename='chartofaccounts')
router.register(r'accounts-v2', AccountV2ViewSet, basename='accountv2')
router.register(r'journal-entries', JournalEntryViewSet, basename='journalentry')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'bank-accounts', BankAccountViewSet, basename='bankaccount')
router.register(r'tax-codes', TaxCodeViewSet, basename='taxcode')
router.register(r'vouchers-v2', VoucherV2ViewSet, basename='voucherv2')

urlpatterns = [
    path('', include(router.urls)),
]
