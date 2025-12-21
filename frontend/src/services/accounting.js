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
};

export default accountingService;
