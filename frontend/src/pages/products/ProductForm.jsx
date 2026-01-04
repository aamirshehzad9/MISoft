import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import productsService from '../../services/products';
import './ProductForm.css';

const ProductForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = Boolean(id);

    const [loading, setLoading] = useState(false);
    const [categories, setCategories] = useState([]);
    const [uoms, setUOMs] = useState([]);
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        description: '',
        product_type: 'raw_material',
        category: '',
        base_uom: '',
        standard_cost: 0,
        selling_price: 0,
        minimum_stock: 0,
        maximum_stock: 0,
        reorder_point: 0,
        is_active: true,
        can_be_sold: false,
        can_be_purchased: true,
        can_be_manufactured: false,
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchCategories();
        fetchUOMs();
        if (isEdit) {
            fetchProduct();
        }
    }, [id]);

    const fetchCategories = async () => {
        try {
            const data = await productsService.getCategories();
            setCategories(data);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const fetchUOMs = async () => {
        try {
            const data = await productsService.getUOMs();
            setUOMs(data);
        } catch (error) {
            console.error('Error fetching UOMs:', error);
        }
    };

    const fetchProduct = async () => {
        try {
            const data = await productsService.getById(id);
            setFormData(data);
        } catch (error) {
            console.error('Error fetching product:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.code.trim()) newErrors.code = 'Product code is required';
        if (!formData.name.trim()) newErrors.name = 'Product name is required';
        if (!formData.base_uom) newErrors.base_uom = 'Unit of measure is required';
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const newErrors = validate();

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            setLoading(true);
            if (isEdit) {
                await productsService.update(id, formData);
            } else {
                await productsService.create(formData);
            }
            navigate('/dashboard/products');
        } catch (error) {
            console.error('Error saving product:', error);
            setErrors({ submit: 'Failed to save product. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const productTypeOptions = [
        { value: 'raw_material', label: 'Raw Material' },
        { value: 'finished_good', label: 'Finished Good' },
        { value: 'semi_finished', label: 'Semi-Finished' },
        { value: 'consumable', label: 'Consumable' },
    ];

    return (
        <div className="product-form-page">
            <Card
                title={isEdit ? 'Edit Product' : 'New Product'}
                subtitle={isEdit ? 'Update product information' : 'Add a new product to inventory'}
            >
                <form onSubmit={handleSubmit} className="product-form">
                    {errors.submit && (
                        <div className="form-error-message">{errors.submit}</div>
                    )}

                    <div className="form-section">
                        <h3 className="form-section-title">Basic Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Product Code"
                                name="code"
                                value={formData.code}
                                onChange={handleChange}
                                error={errors.code}
                                required
                                helperText="Unique identifier for the product"
                            />
                            <Input
                                label="Product Name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                error={errors.name}
                                required
                            />
                            <Select
                                label="Product Type"
                                name="product_type"
                                value={formData.product_type}
                                onChange={handleChange}
                                options={productTypeOptions}
                                required
                            />
                            <Select
                                label="Category"
                                name="category"
                                value={formData.category}
                                onChange={handleChange}
                                options={categories.map(cat => ({ value: cat.id, label: cat.name }))}
                                placeholder="Select category"
                            />
                            <Input
                                label="Description"
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                className="form-grid-full"
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Unit of Measure</h3>
                        <div className="form-grid">
                            <Select
                                label="Base UOM"
                                name="base_uom"
                                value={formData.base_uom}
                                onChange={handleChange}
                                options={uoms.map(uom => ({ value: uom.id, label: `${uom.name} (${uom.symbol})` }))}
                                error={errors.base_uom}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Pricing</h3>
                        <div className="form-grid">
                            <Input
                                label="Standard Cost"
                                name="standard_cost"
                                type="number"
                                step="0.01"
                                value={formData.standard_cost}
                                onChange={handleChange}
                                helperText="Cost price per unit"
                            />
                            <Input
                                label="Selling Price"
                                name="selling_price"
                                type="number"
                                step="0.01"
                                value={formData.selling_price}
                                onChange={handleChange}
                                helperText="Sales price per unit"
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Inventory Management</h3>
                        <div className="form-grid">
                            <Input
                                label="Minimum Stock"
                                name="minimum_stock"
                                type="number"
                                value={formData.minimum_stock}
                                onChange={handleChange}
                            />
                            <Input
                                label="Maximum Stock"
                                name="maximum_stock"
                                type="number"
                                value={formData.maximum_stock}
                                onChange={handleChange}
                            />
                            <Input
                                label="Reorder Point"
                                name="reorder_point"
                                type="number"
                                value={formData.reorder_point}
                                onChange={handleChange}
                                helperText="Stock level to trigger reorder"
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Product Settings</h3>
                        <div className="checkbox-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="can_be_sold"
                                    checked={formData.can_be_sold}
                                    onChange={handleChange}
                                />
                                <span>Can be Sold</span>
                            </label>
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="can_be_purchased"
                                    checked={formData.can_be_purchased}
                                    onChange={handleChange}
                                />
                                <span>Can be Purchased</span>
                            </label>
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="can_be_manufactured"
                                    checked={formData.can_be_manufactured}
                                    onChange={handleChange}
                                />
                                <span>Can be Manufactured</span>
                            </label>
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                />
                                <span>Active</span>
                            </label>
                        </div>
                    </div>

                    <div className="form-actions">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => navigate('/dashboard/products')}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="primary"
                            loading={loading}
                        >
                            {isEdit ? 'Update Product' : 'Create Product'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default ProductForm;
