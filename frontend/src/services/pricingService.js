import api from './api';

const pricingService = {
  // Rules
  getRules: (params) => api.get('/pricing/rules/', { params }),
  getRule: (id) => api.get(`/pricing/rules/${id}/`),
  createRule: (data) => api.post('/pricing/rules/', data),
  updateRule: (id, data) => api.put(`/pricing/rules/${id}/`, data),
  partiallyUpdateRule: (id, data) => api.patch(`/pricing/rules/${id}/`, data),
  deleteRule: (id) => api.delete(`/pricing/rules/${id}/`),
  
  // Actions
  calculatePrice: (data) => api.post('/pricing/rules/calculate/', data),
  bulkImport: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/pricing/rules/bulk_import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  exportTemplate: () => api.get('/pricing/rules/export_template/', { responseType: 'blob' }),
  
  // Reports
  getReportByProduct: (params) => api.get('/pricing/rules/report_by_product/', { params }),
  getReportByCustomer: (params) => api.get('/pricing/rules/report_by_customer/', { params }),
  getReportPriceHistory: (params) => api.get('/pricing/rules/report_price_history/', { params }),
  getReportPriceVariance: (params) => api.get('/pricing/rules/report_price_variance/', { params })
};

export default pricingService;
