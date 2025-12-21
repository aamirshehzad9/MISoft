import api from './api';

export const partnersService = {
    // Get all partners
    getAll: async (params = {}) => {
        const response = await api.get('/partners/', { params });
        return response.data;
    },

    // Get partner by ID
    getById: async (id) => {
        const response = await api.get(`/partners/${id}/`);
        return response.data;
    },

    // Create partner
    create: async (data) => {
        const response = await api.post('/partners/', data);
        return response.data;
    },

    // Update partner
    update: async (id, data) => {
        const response = await api.put(`/partners/${id}/`, data);
        return response.data;
    },

    // Delete partner
    delete: async (id) => {
        const response = await api.delete(`/partners/${id}/`);
        return response.data;
    },

    // Get customers only
    getCustomers: async () => {
        const response = await api.get('/partners/customers/');
        return response.data;
    },

    // Get vendors only
    getVendors: async () => {
        const response = await api.get('/partners/vendors/');
        return response.data;
    },

    // Toggle active status
    toggleActive: async (id) => {
        const response = await api.post(`/partners/${id}/toggle_active/`);
        return response.data;
    },
};

export default partnersService;
