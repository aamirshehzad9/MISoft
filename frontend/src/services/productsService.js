import api from './api';

const productsService = {
  // UoM Conversions
  convertUoM: (data) => api.post('/products/uom-conversions/convert/', data),
  
  bulkConvertUoM: (conversions) => api.post('/products/uom-conversions/bulk_convert/', { conversions }),
  
  getAvailableConversions: (fromUomId) => 
    api.get(`/products/uom-conversions/available_conversions/?from_uom_id=${fromUomId}`),
  
  listUoMConversions: (params) => api.get('/products/uom-conversions/', { params }),
  
  createUoMConversion: (data) => api.post('/products/uom-conversions/', data),
  
  updateUoMConversion: (id, data) => api.put(`/products/uom-conversions/${id}/`, data),
  
  deleteUoMConversion: (id) => api.delete(`/products/uom-conversions/${id}/`),
  
  // Units of Measure
  listUnitsOfMeasure: (params) => api.get('/products/units-of-measure/', { params }),
  
  getUnitOfMeasure: (id) => api.get(`/products/units-of-measure/${id}/`),
  
  // Product Variants
  createVariantQuick: (data) => api.post('/products/variants/quick-create/', data),
};

export default productsService;

// Named exports for easier testing
export const { createVariantQuick } = productsService;
