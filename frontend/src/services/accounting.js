import api from './api';

export const accountingService = {
    // Invoices
    getInvoices: async (params = {}) => {
        const response = await api.get('/accounting/invoices/', { params });
        return response.data;
    },

    getInvoiceById: async (id) => {
        const response = await api.get(`/accounting/invoices/${id}/`);
        return response.data;
    },

    createInvoice: async (data) => {
        const response = await api.post('/accounting/invoices/', data);
        return response.data;
    },

    updateInvoice: async (id, data) => {
        const response = await api.put(`/accounting/invoices/${id}/`, data);
        return response.data;
    },

    submitInvoice: async (id) => {
        const response = await api.post(`/accounting/invoices/${id}/submit_invoice/`);
        return response.data;
    },

    getSalesInvoices: async () => {
        const response = await api.get('/accounting/invoices/sales_invoices/');
        return response.data;
    },

    getPurchaseInvoices: async () => {
        const response = await api.get('/accounting/invoices/purchase_invoices/');
        return response.data;
    },

    getOverdueInvoices: async () => {
        const response = await api.get('/accounting/invoices/overdue/');
        return response.data;
    },

    // Payments
    getPayments: async (params = {}) => {
        const response = await api.get('/accounting/payments/', { params });
        return response.data;
    },

    createPayment: async (data) => {
        const response = await api.post('/accounting/payments/', data);
        return response.data;
    },

    getReceipts: async () => {
        const response = await api.get('/accounting/payments/receipts/');
        return response.data;
    },

    getPaymentsMade: async () => {
        const response = await api.get('/accounting/payments/payments_made/');
        return response.data;
    },

    // Bank Accounts
    getBankAccounts: async () => {
        const response = await api.get('/accounting/bank-accounts/');
        return response.data;
    },

    // Chart of Accounts
    getChartOfAccounts: async () => {
        const response = await api.get('/accounting/chart-of-accounts/');
        return response.data;
    },

    getAccountsV2: async () => {
        const response = await api.get('/accounting/accounts-v2/hierarchy/');
        return response.data;
    },

    // Account V2 CRUD
    getAccountById: async (id) => {
        const response = await api.get(`/accounting/accounts-v2/${id}/`);
        return response.data;
    },

    createAccount: async (data) => {
        const response = await api.post('/accounting/accounts-v2/', data);
        return response.data;
    },

    updateAccount: async (id, data) => {
        const response = await api.put(`/accounting/accounts-v2/${id}/`, data);
        return response.data;
    },

    deleteAccount: async (id) => {
        const response = await api.delete(`/accounting/accounts-v2/${id}/`);
        return response.data;
    },

    // Journal Entries
    getJournalEntries: async (params = {}) => {
        const response = await api.get('/accounting/journal-entries/', { params });
        return response.data;
    },

    createJournalEntry: async (data) => {
        const response = await api.post('/accounting/journal-entries/', data);
        return response.data;
    },

    postJournalEntry: async (id) => {
        const response = await api.post(`/accounting/journal-entries/${id}/post_entry/`);
        return response.data;
    },

    // Vouchers (V2)
    getVouchers: async (params = {}) => {
        const response = await api.get('/accounting/vouchers-v2/', { params });
        return response.data;
    },

    getVoucherById: async (id) => {
        const response = await api.get(`/accounting/vouchers-v2/${id}/`);
        return response.data;
    },

    createVoucher: async (data) => {
        const response = await api.post('/accounting/vouchers-v2/', data);
        return response.data;
    },

    postVoucher: async (id) => {
        const response = await api.post(`/accounting/vouchers-v2/${id}/post/`);
        return response.data;
    },

    // Numbering Schemes
    getNumberingSchemes: async (params = {}) => {
        const response = await api.get('/accounting/numbering-schemes/', { params });
        return response.data;
    },

    getNumberingSchemeById: async (id) => {
        const response = await api.get(`/accounting/numbering-schemes/${id}/`);
        return response.data;
    },

    createNumberingScheme: async (data) => {
        const response = await api.post('/accounting/numbering-schemes/', data);
        return response.data;
    },

    updateNumberingScheme: async (id, data) => {
        const response = await api.put(`/accounting/numbering-schemes/${id}/`, data);
        return response.data;
    },

    deleteNumberingScheme: async (id) => {
        const response = await api.delete(`/accounting/numbering-schemes/${id}/`);
        return response.data;
    },

    generateNumber: async (data) => {
        const response = await api.post('/accounting/numbering-schemes/generate/', data);
        return response.data;
    },

    previewNumber: async (data) => {
        const response = await api.post('/accounting/numbering-schemes/preview/', data);
        return response.data;
    },

    resetCounter: async (id, data = {}) => {
        const response = await api.post(`/accounting/numbering-schemes/${id}/reset/`, data);
        return response.data;
    },

    getSchemeInfo: async (params) => {
        const response = await api.get('/accounting/numbering-schemes/info/', { params });
        return response.data;
    },

    // Reference Definitions
    getReferenceDefinitions: async (modelName) => {
        const params = {};
        if (modelName) params.model_name = modelName;
        const response = await api.get('/accounting/reference-definitions/', { params });
        return response.data;
    },

    // ============================================================================
    // MODULE 2.2: CHEQUE MANAGEMENT SYSTEM - API METHODS
    // ============================================================================

    // Cheques
    getCheques: async (params = {}) => {
        const response = await api.get('/accounting/cheques/', { params });
        return response.data;
    },

    getChequeById: async (id) => {
        const response = await api.get(`/accounting/cheques/${id}/`);
        return response.data;
    },

    createCheque: async (data) => {
        const response = await api.post('/accounting/cheques/', data);
        return response.data;
    },

    updateCheque: async (id, data) => {
        const response = await api.put(`/accounting/cheques/${id}/`, data);
        return response.data;
    },

    deleteCheque: async (id) => {
        const response = await api.delete(`/accounting/cheques/${id}/`);
        return response.data;
    },

    clearCheque: async (id, clearanceDate) => {
        const response = await api.post(`/accounting/cheques/${id}/clear/`, {
            clearance_date: clearanceDate
        });
        return response.data;
    },

    cancelCheque: async (id, cancelledDate, reason) => {
        const response = await api.post(`/accounting/cheques/${id}/cancel/`, {
            cancelled_date: cancelledDate,
            cancellation_reason: reason
        });
        return response.data;
    },

    printCheque: async (id) => {
        const response = await api.get(`/accounting/cheques/${id}/print/`, {
            responseType: 'blob'
        });
        return response.data;
    },

    getPostDatedCheques: async () => {
        const response = await api.get('/accounting/cheques/post-dated/');
        return response.data;
    },

    // ============================================================================
    // MODULE 2.3: BANK TRANSFER SYSTEM - API METHODS
    // ============================================================================

    // Bank Transfers
    getBankTransfers: async (params = {}) => {
        const response = await api.get('/accounting/bank-transfers/', { params });
        return response.data;
    },

    getBankTransferById: async (id) => {
        const response = await api.get(`/accounting/bank-transfers/${id}/`);
        return response.data;
    },

    createBankTransfer: async (data) => {
        const response = await api.post('/accounting/bank-transfers/', data);
        return response.data;
    },

    updateBankTransfer: async (id, data) => {
        const response = await api.put(`/accounting/bank-transfers/${id}/`, data);
        return response.data;
    },

    deleteBankTransfer: async (id) => {
        const response = await api.delete(`/accounting/bank-transfers/${id}/`);
        return response.data;
    },

    approveBankTransfer: async (id) => {
        const response = await api.post(`/accounting/bank-transfers/${id}/approve/`);
        return response.data;
    },

    rejectBankTransfer: async (id) => {
        const response = await api.post(`/accounting/bank-transfers/${id}/reject/`);
        return response.data;
    },

    executeBankTransfer: async (id, fxAccountId = null) => {
        const data = {};
        if (fxAccountId) data.fx_account_id = fxAccountId;
        const response = await api.post(`/accounting/bank-transfers/${id}/execute/`, data);
        return response.data;
    },

    getPendingBankTransfers: async () => {
        const response = await api.get('/accounting/bank-transfers/pending/');
        return response.data;
    },

    // ============================================================================
    // MODULE 2.1: BANK RECONCILIATION SYSTEM - API METHODS
    // ============================================================================

    // Bank Reconciliations
    getBankReconciliations: async (params = {}) => {
        const response = await api.get('/accounting/bank-reconciliations/', { params });
        return response.data;
    },

    getBankReconciliationById: async (id) => {
        const response = await api.get(`/accounting/bank-reconciliations/${id}/`);
        return response.data;
    },

    createBankReconciliation: async (data) => {
        const response = await api.post('/accounting/bank-reconciliations/', data);
        return response.data;
    },

    updateBankReconciliation: async (id, data) => {
        const response = await api.put(`/accounting/bank-reconciliations/${id}/`, data);
        return response.data;
    },

    deleteBankReconciliation: async (id) => {
        const response = await api.delete(`/accounting/bank-reconciliations/${id}/`);
        return response.data;
    },

    getBankReconciliationSummary: async (id) => {
        const response = await api.get(`/accounting/bank-reconciliations/${id}/summary/`);
        return response.data;
    },

    getBRSReport: async (id) => {
        const response = await api.get(`/accounting/bank-reconciliations/${id}/brs-report/`);
        return response.data;
    },

    // ============================================================================
    // MODULE 1.7: AUDIT TRAIL SYSTEM - API METHODS
    // ============================================================================

    // Audit Logs
    getAuditLogs: async (params = {}) => {
        const response = await api.get('/accounting/audit-logs/', { params });
        return response.data;
    },

    getAuditLogById: async (id) => {
        const response = await api.get(`/accounting/audit-logs/${id}/`);
        return response.data;
    },

    exportAuditLogsPDF: async (params = {}) => {
        const response = await api.get('/accounting/audit-logs/export-pdf/', {
            params,
            responseType: 'blob'
        });
        return response.data;
    },

    // ============================================================================
    // MODULE 3.1: FIXED ASSET REGISTER - API METHODS
    // ============================================================================

    // Asset Categories
    getAssetCategories: async (params = {}) => {
        const response = await api.get('/accounting/asset-categories/', { params });
        return response.data;
    },

    getAssetCategoryById: async (id) => {
        const response = await api.get(`/accounting/asset-categories/${id}/`);
        return response.data;
    },

    createAssetCategory: async (data) => {
        const response = await api.post('/accounting/asset-categories/', data);
        return response.data;
    },

    updateAssetCategory: async (id, data) => {
        const response = await api.put(`/accounting/asset-categories/${id}/`, data);
        return response.data;
    },

    deleteAssetCategory: async (id) => {
        const response = await api.delete(`/accounting/asset-categories/${id}/`);
        return response.data;
    },

    // Fixed Assets
    getFixedAssets: async (params = {}) => {
        const response = await api.get('/accounting/fixed-assets/', { params });
        return response.data;
    },

    getFixedAssetById: async (id) => {
        const response = await api.get(`/accounting/fixed-assets/${id}/`);
        return response.data;
    },

    createFixedAsset: async (data) => {
        const response = await api.post('/accounting/fixed-assets/', data);
        return response.data;
    },

    updateFixedAsset: async (id, data) => {
        const response = await api.put(`/accounting/fixed-assets/${id}/`, data);
        return response.data;
    },

    deleteFixedAsset: async (id) => {
        const response = await api.delete(`/accounting/fixed-assets/${id}/`);
        return response.data;
    },

    disposeFixedAsset: async (id, disposalDate, disposalAmount) => {
        const response = await api.post(`/accounting/fixed-assets/${id}/dispose/`, {
            disposal_date: disposalDate,
            disposal_amount: disposalAmount
        });
        return response.data;
    },

    getAssetsByLocation: async () => {
        const response = await api.get('/accounting/fixed-assets/by_location/');
        return response.data;
    },

    getAssetsByCategory: async () => {
        const response = await api.get('/accounting/fixed-assets/by_category/');
        return response.data;
    },

    // Asset Reports
    getFixedAssetRegister: async (params = {}) => {
        const response = await api.get('/accounting/reports/fixed-asset-register/', { params });
        return response.data;
    },

    getAssetsByCategoryReport: async () => {
        const response = await api.get('/accounting/reports/assets-by-category/');
        return response.data;
    },

    getAssetsByLocationReport: async () => {
        const response = await api.get('/accounting/reports/assets-by-location/');
        return response.data;
    },

    // ============================================================================
    // FISCAL YEAR MANAGEMENT - API METHODS
    // ============================================================================

    // Fiscal Years
    getFiscalYears: async (params = {}) => {
        const response = await api.get('/accounting/fiscal-years/', { params });
        return response.data;
    },

    getFiscalYearById: async (id) => {
        const response = await api.get(`/accounting/fiscal-years/${id}/`);
        return response.data;
    },

    createFiscalYear: async (data) => {
        const response = await api.post('/accounting/fiscal-years/', data);
        return response.data;
    },

    updateFiscalYear: async (id, data) => {
        const response = await api.put(`/accounting/fiscal-years/${id}/`, data);
        return response.data;
    },

    deleteFiscalYear: async (id) => {
        const response = await api.delete(`/accounting/fiscal-years/${id}/`);
        return response.data;
    },

    // ============================================================================
    // TAX CODE MANAGEMENT - API METHODS
    // ============================================================================

    // Tax Codes
    getTaxCodes: async (params = {}) => {
        const response = await api.get('/accounting/tax-codes/', { params });
        return response.data;
    },

    getTaxCodeById: async (id) => {
        const response = await api.get(`/accounting/tax-codes/${id}/`);
        return response.data;
    },

    createTaxCode: async (data) => {
        const response = await api.post('/accounting/tax-codes/', data);
        return response.data;
    },

    updateTaxCode: async (id, data) => {
        const response = await api.put(`/accounting/tax-codes/${id}/`, data);
        return response.data;
    },

    deleteTaxCode: async (id) => {
        const response = await api.delete(`/accounting/tax-codes/${id}/`);
        return response.data;
    },

    // ============================================================================
    // TAX MASTER V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Tax Masters V2
    getTaxMasters: async (params = {}) => {
        const response = await api.get('/accounting/tax-masters-v2/', { params });
        return response.data;
    },

    getTaxMasterById: async (id) => {
        const response = await api.get(`/accounting/tax-masters-v2/${id}/`);
        return response.data;
    },

    createTaxMaster: async (data) => {
        const response = await api.post('/accounting/tax-masters-v2/', data);
        return response.data;
    },

    updateTaxMaster: async (id, data) => {
        const response = await api.put(`/accounting/tax-masters-v2/${id}/`, data);
        return response.data;
    },

    deleteTaxMaster: async (id) => {
        const response = await api.delete(`/accounting/tax-masters-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // TAX GROUP V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Tax Groups V2
    getTaxGroups: async (params = {}) => {
        const response = await api.get('/accounting/tax-groups-v2/', { params });
        return response.data;
    },

    getTaxGroupById: async (id) => {
        const response = await api.get(`/accounting/tax-groups-v2/${id}/`);
        return response.data;
    },

    createTaxGroup: async (data) => {
        const response = await api.post('/accounting/tax-groups-v2/', data);
        return response.data;
    },

    updateTaxGroup: async (id, data) => {
        const response = await api.put(`/accounting/tax-groups-v2/${id}/`, data);
        return response.data;
    },

    deleteTaxGroup: async (id) => {
        const response = await api.delete(`/accounting/tax-groups-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // CURRENCY V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Currencies V2
    getCurrencies: async (params = {}) => {
        const response = await api.get('/accounting/currencies-v2/', { params });
        return response.data;
    },

    getCurrencyById: async (id) => {
        const response = await api.get(`/accounting/currencies-v2/${id}/`);
        return response.data;
    },

    createCurrency: async (data) => {
        const response = await api.post('/accounting/currencies-v2/', data);
        return response.data;
    },

    updateCurrency: async (id, data) => {
        const response = await api.put(`/accounting/currencies-v2/${id}/`, data);
        return response.data;
    },

    deleteCurrency: async (id) => {
        const response = await api.delete(`/accounting/currencies-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // EXCHANGE RATE V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Exchange Rates V2
    getExchangeRates: async (params = {}) => {
        const response = await api.get('/accounting/exchange-rates-v2/', { params });
        return response.data;
    },

    getExchangeRateById: async (id) => {
        const response = await api.get(`/accounting/exchange-rates-v2/${id}/`);
        return response.data;
    },

    createExchangeRate: async (data) => {
        const response = await api.post('/accounting/exchange-rates-v2/', data);
        return response.data;
    },

    updateExchangeRate: async (id, data) => {
        const response = await api.put(`/accounting/exchange-rates-v2/${id}/`, data);
        return response.data;
    },

    deleteExchangeRate: async (id) => {
        const response = await api.delete(`/accounting/exchange-rates-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // COST CENTER V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Cost Centers V2
    getCostCenters: async (params = {}) => {
        const response = await api.get('/accounting/cost-centers-v2/', { params });
        return response.data;
    },

    getCostCenterById: async (id) => {
        const response = await api.get(`/accounting/cost-centers-v2/${id}/`);
        return response.data;
    },

    createCostCenter: async (data) => {
        const response = await api.post('/accounting/cost-centers-v2/', data);
        return response.data;
    },

    updateCostCenter: async (id, data) => {
        const response = await api.put(`/accounting/cost-centers-v2/${id}/`, data);
        return response.data;
    },

    deleteCostCenter: async (id) => {
        const response = await api.delete(`/accounting/cost-centers-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // DEPARTMENT V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Departments V2
    getDepartments: async (params = {}) => {
        const response = await api.get('/accounting/departments-v2/', { params });
        return response.data;
    },

    getDepartmentById: async (id) => {
        const response = await api.get(`/accounting/departments-v2/${id}/`);
        return response.data;
    },

    createDepartment: async (data) => {
        const response = await api.post('/accounting/departments-v2/', data);
        return response.data;
    },

    updateDepartment: async (id, data) => {
        const response = await api.put(`/accounting/departments-v2/${id}/`, data);
        return response.data;
    },

    deleteDepartment: async (id) => {
        const response = await api.delete(`/accounting/departments-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // ENTITY V2 MANAGEMENT - API METHODS
    // ============================================================================

    // Entities V2
    getEntities: async (params = {}) => {
        const response = await api.get('/accounting/entities-v2/', { params });
        return response.data;
    },

    getEntityById: async (id) => {
        const response = await api.get(`/accounting/entities-v2/${id}/`);
        return response.data;
    },

    createEntity: async (data) => {
        const response = await api.post('/accounting/entities-v2/', data);
        return response.data;
    },

    updateEntity: async (id, data) => {
        const response = await api.put(`/accounting/entities-v2/${id}/`, data);
        return response.data;
    },

    deleteEntity: async (id) => {
        const response = await api.delete(`/accounting/entities-v2/${id}/`);
        return response.data;
    },

    // ============================================================================
    // BANK ACCOUNT MANAGEMENT - API METHODS
    // ============================================================================

    // Bank Accounts
    getBankAccounts: async (params = {}) => {
        const response = await api.get('/accounting/bank-accounts/', { params });
        return response.data;
    },

    getBankAccountById: async (id) => {
        const response = await api.get(`/accounting/bank-accounts/${id}/`);
        return response.data;
    },

    createBankAccount: async (data) => {
        const response = await api.post('/accounting/bank-accounts/', data);
        return response.data;
    },

    updateBankAccount: async (id, data) => {
        const response = await api.put(`/accounting/bank-accounts/${id}/`, data);
        return response.data;
    },

    deleteBankAccount: async (id) => {
        const response = await api.delete(`/accounting/bank-accounts/${id}/`);
        return response.data;
    },

    // ============================================================================
    // BANK STATEMENT MANAGEMENT - API METHODS
    // ============================================================================

    // Bank Statements
    getBankStatements: async (params = {}) => {
        const response = await api.get('/accounting/bank-statements/', { params });
        return response.data;
    },

    getBankStatementById: async (id) => {
        const response = await api.get(`/accounting/bank-statements/${id}/`);
        return response.data;
    },

    createBankStatement: async (data) => {
        const response = await api.post('/accounting/bank-statements/', data);
        return response.data;
    },

    updateBankStatement: async (id, data) => {
        const response = await api.put(`/accounting/bank-statements/${id}/`, data);
        return response.data;
    },

    deleteBankStatement: async (id) => {
        const response = await api.delete(`/accounting/bank-statements/${id}/`);
        return response.data;
    },

    // ============================================================================
    // FAIR VALUE MEASUREMENT - API METHODS (IAS 39/IFRS 9)
    // ============================================================================

    // Fair Value Measurements
    getFairValueMeasurements: async (params = {}) => {
        const response = await api.get('/accounting/fair-value-measurements/', { params });
        return response.data;
    },

    getFairValueMeasurementById: async (id) => {
        const response = await api.get(`/accounting/fair-value-measurements/${id}/`);
        return response.data;
    },

    createFairValueMeasurement: async (data) => {
        const response = await api.post('/accounting/fair-value-measurements/', data);
        return response.data;
    },

    updateFairValueMeasurement: async (id, data) => {
        const response = await api.put(`/accounting/fair-value-measurements/${id}/`, data);
        return response.data;
    },

    deleteFairValueMeasurement: async (id) => {
        const response = await api.delete(`/accounting/fair-value-measurements/${id}/`);
        return response.data;
    },

    // ============================================================================
    // FX REVALUATION LOG - API METHODS (IAS 21)
    // ============================================================================

    // FX Revaluation Logs
    getFXRevaluationLogs: async (params = {}) => {
        const response = await api.get('/accounting/fx-revaluation-logs/', { params });
        return response.data;
    },

    getFXRevaluationLogById: async (id) => {
        const response = await api.get(`/accounting/fx-revaluation-logs/${id}/`);
        return response.data;
    },

    createFXRevaluationLog: async (data) => {
        const response = await api.post('/accounting/fx-revaluation-logs/', data);
        return response.data;
    },

    updateFXRevaluationLog: async (id, data) => {
        const response = await api.put(`/accounting/fx-revaluation-logs/${id}/`, data);
        return response.data;
    },

    deleteFXRevaluationLog: async (id) => {
        const response = await api.delete(`/accounting/fx-revaluation-logs/${id}/`);
        return response.data;
    },
};

export default accountingService;

