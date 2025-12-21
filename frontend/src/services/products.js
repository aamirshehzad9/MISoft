import api from './api';

export const productsService = {
    // Products
    getAll: async (params = {}) => {
        const response = await api.get('/products/', { params });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/products/${id}/`);
        return response.data;
    },

    create: async (data) => {
        const response = await api.post('/products/', data);
        return response.data;
    },

    update: async (id, data) => {
        const response = await api.put(`/products/${id}/`, data);
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/products/${id}/`);
        return response.data;
    },

    getRawMaterials: async () => {
        const response = await api.get('/products/raw_materials/');
        return response.data;
    },

    getFinishedGoods: async () => {
        const response = await api.get('/products/finished_goods/');
        return response.data;
    },

    // Categories
    getCategories: async () => {
        const response = await api.get('/categories/');
        return response.data;
    },

    createCategory: async (data) => {
        const response = await api.post('/categories/', data);
        return response.data;
    },

    // Units of Measure
    getUOMs: async () => {
        const response = await api.get('/uom/');
        return response.data;
    },
};

export default productsService;
