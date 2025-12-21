import api from './api';

export const manufacturingService = {
    // BOM
    getBOMs: async (params = {}) => {
        const response = await api.get('/manufacturing/bom/', { params });
        return response.data;
    },

    getBOMById: async (id) => {
        const response = await api.get(`/manufacturing/bom/${id}/`);
        return response.data;
    },

    createBOM: async (data) => {
        const response = await api.post('/manufacturing/bom/', data);
        return response.data;
    },

    // Production Orders
    getProductionOrders: async (params = {}) => {
        const response = await api.get('/manufacturing/production-orders/', { params });
        return response.data;
    },

    getProductionOrderById: async (id) => {
        const response = await api.get(`/manufacturing/production-orders/${id}/`);
        return response.data;
    },

    createProductionOrder: async (data) => {
        const response = await api.post('/manufacturing/production-orders/', data);
        return response.data;
    },

    updateProductionOrder: async (id, data) => {
        const response = await api.put(`/manufacturing/production-orders/${id}/`, data);
        return response.data;
    },

    startProduction: async (id) => {
        const response = await api.post(`/manufacturing/production-orders/${id}/start_production/`);
        return response.data;
    },

    completeProduction: async (id) => {
        const response = await api.post(`/manufacturing/production-orders/${id}/complete_production/`);
        return response.data;
    },

    recordProduction: async (id, data) => {
        const response = await api.post(`/manufacturing/production-orders/${id}/record_production/`, data);
        return response.data;
    },

    getInProgressOrders: async () => {
        const response = await api.get('/manufacturing/production-orders/in_progress/');
        return response.data;
    },

    // Work Centers
    getWorkCenters: async () => {
        const response = await api.get('/manufacturing/work-centers/');
        return response.data;
    },
};

export default manufacturingService;
