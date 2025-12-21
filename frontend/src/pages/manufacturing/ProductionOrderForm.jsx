import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import manufacturingService from '../../services/manufacturing';
import productsService from '../../services/products';
import './ProductionOrderForm.css';

const ProductionOrderForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = Boolean(id);

    const [loading, setLoading] = useState(false);
    const [products, setProducts] = useState([]);
    const [boms, setBOMs] = useState([]);
    const [workCenters, setWorkCenters] = useState([]);
    const [formData, setFormData] = useState({
        order_number: '',
        product: '',
        bom: '',
        work_center: '',
        planned_quantity: 1,
        planned_start_date: new Date().toISOString().split('T')[0],
        planned_end_date: new Date().toISOString().split('T')[0],
        priority: 'normal',
        notes: '',
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchProducts();
        fetchBOMs();
        fetchWorkCenters();
        if (isEdit) {
            fetchProductionOrder();
        } else {
            generateOrderNumber();
        }
    }, [id]);

    const generateOrderNumber = () => {
        const timestamp = Date.now();
        const orderNum = `PO-${timestamp.toString().slice(-8)}`;
        setFormData(prev => ({ ...prev, order_number: orderNum }));
    };

    const fetchProducts = async () => {
        try {
            const data = await productsService.getFinishedGoods();
            setProducts(data);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };

    const fetchBOMs = async () => {
        try {
            const data = await manufacturingService.getBOMs();
            setBOMs(data);
        } catch (error) {
            console.error('Error fetching BOMs:', error);
        }
    };

    const fetchWorkCenters = async () => {
        try {
            const data = await manufacturingService.getWorkCenters();
            setWorkCenters(data);
        } catch (error) {
            console.error('Error fetching work centers:', error);
        }
    };

    const fetchProductionOrder = async () => {
        try {
            const data = await manufacturingService.getProductionOrderById(id);
            setFormData({
                ...data,
                planned_start_date: data.planned_start_date?.split('T')[0] || '',
                planned_end_date: data.planned_end_date?.split('T')[0] || '',
            });
        } catch (error) {
            console.error('Error fetching production order:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.order_number.trim()) newErrors.order_number = 'Order number is required';
        if (!formData.product) newErrors.product = 'Product is required';
        if (!formData.bom) newErrors.bom = 'BOM is required';
        if (!formData.planned_quantity || formData.planned_quantity <= 0) {
            newErrors.planned_quantity = 'Quantity must be greater than 0';
        }
        if (!formData.planned_start_date) newErrors.planned_start_date = 'Start date is required';
        if (!formData.planned_end_date) newErrors.planned_end_date = 'End date is required';
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
                await manufacturingService.updateProductionOrder(id, formData);
            } else {
                await manufacturingService.createProductionOrder(formData);
            }
            navigate('/manufacturing/production-orders');
        } catch (error) {
            console.error('Error saving production order:', error);
            setErrors({ submit: 'Failed to save production order. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const priorityOptions = [
        { value: 'low', label: 'Low' },
        { value: 'normal', label: 'Normal' },
        { value: 'high', label: 'High' },
        { value: 'urgent', label: 'Urgent' },
    ];

    return (
        <div className="production-order-form-page">
            <Card
                title={isEdit ? 'Edit Production Order' : 'New Production Order'}
                subtitle={isEdit ? 'Update production order details' : 'Create a new manufacturing work order'}
            >
                <form onSubmit={handleSubmit} className="production-order-form">
                    {errors.submit && (
                        <div className="form-error-message">{errors.submit}</div>
                    )}

                    <div className="form-section">
                        <h3 className="form-section-title">Order Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Order Number"
                                name="order_number"
                                value={formData.order_number}
                                onChange={handleChange}
                                error={errors.order_number}
                                required
                                disabled={isEdit}
                            />
                            <Select
                                label="Priority"
                                name="priority"
                                value={formData.priority}
                                onChange={handleChange}
                                options={priorityOptions}
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Product & BOM</h3>
                        <div className="form-grid">
                            <Select
                                label="Product"
                                name="product"
                                value={formData.product}
                                onChange={handleChange}
                                options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))}
                                error={errors.product}
                                required
                            />
                            <Select
                                label="Bill of Materials"
                                name="bom"
                                value={formData.bom}
                                onChange={handleChange}
                                options={boms.map(b => ({ value: b.id, label: `${b.product_name} (v${b.version})` }))}
                                error={errors.bom}
                                required
                            />
                            <Select
                                label="Work Center"
                                name="work_center"
                                value={formData.work_center}
                                onChange={handleChange}
                                options={workCenters.map(wc => ({ value: wc.id, label: wc.name }))}
                                placeholder="Select work center"
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Quantity & Schedule</h3>
                        <div className="form-grid">
                            <Input
                                label="Planned Quantity"
                                name="planned_quantity"
                                type="number"
                                value={formData.planned_quantity}
                                onChange={handleChange}
                                error={errors.planned_quantity}
                                required
                            />
                            <Input
                                label="Planned Start Date"
                                name="planned_start_date"
                                type="date"
                                value={formData.planned_start_date}
                                onChange={handleChange}
                                error={errors.planned_start_date}
                                required
                            />
                            <Input
                                label="Planned End Date"
                                name="planned_end_date"
                                type="date"
                                value={formData.planned_end_date}
                                onChange={handleChange}
                                error={errors.planned_end_date}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Additional Notes</h3>
                        <div className="form-grid">
                            <Input
                                label="Notes"
                                name="notes"
                                value={formData.notes}
                                onChange={handleChange}
                                className="form-grid-full"
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => navigate('/manufacturing/production-orders')}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="primary"
                            loading={loading}
                        >
                            {isEdit ? 'Update Order' : 'Create Order'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default ProductionOrderForm;
