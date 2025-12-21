import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import accountingService from '../../services/accounting';
import partnersService from '../../services/partners';
import productsService from '../../services/products';
import './InvoiceForm.css';

const InvoiceForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = Boolean(id);

    const [loading, setLoading] = useState(false);
    const [partners, setPartners] = useState([]);
    const [products, setProducts] = useState([]);
    const [formData, setFormData] = useState({
        invoice_number: '',
        invoice_type: 'sales',
        partner: '',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: new Date().toISOString().split('T')[0],
        payment_terms: '',
        notes: '',
    });
    const [lineItems, setLineItems] = useState([
        { product: '', description: '', quantity: 1, unit_price: 0, tax_rate: 0 }
    ]);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchPartners();
        fetchProducts();
        if (isEdit) {
            fetchInvoice();
        } else {
            generateInvoiceNumber();
        }
    }, [id]);

    const generateInvoiceNumber = () => {
        const timestamp = Date.now();
        const invoiceNum = `INV-${timestamp.toString().slice(-8)}`;
        setFormData(prev => ({ ...prev, invoice_number: invoiceNum }));
    };

    const fetchPartners = async () => {
        try {
            const data = await partnersService.getAll();
            setPartners(data);
        } catch (error) {
            console.error('Error fetching partners:', error);
        }
    };

    const fetchProducts = async () => {
        try {
            const data = await productsService.getAll();
            setProducts(data);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };

    const fetchInvoice = async () => {
        try {
            const data = await accountingService.getInvoiceById(id);
            setFormData({
                ...data,
                invoice_date: data.invoice_date?.split('T')[0] || '',
                due_date: data.due_date?.split('T')[0] || '',
            });
            if (data.items && data.items.length > 0) {
                setLineItems(data.items);
            }
        } catch (error) {
            console.error('Error fetching invoice:', error);
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

    const handleLineItemChange = (index, field, value) => {
        const newLineItems = [...lineItems];
        newLineItems[index][field] = value;

        // Auto-fill description and price when product is selected
        if (field === 'product' && value) {
            const product = products.find(p => p.id === parseInt(value));
            if (product) {
                newLineItems[index].description = product.name;
                newLineItems[index].unit_price = product.selling_price || 0;
            }
        }

        setLineItems(newLineItems);
    };

    const addLineItem = () => {
        setLineItems([...lineItems, { product: '', description: '', quantity: 1, unit_price: 0, tax_rate: 0 }]);
    };

    const removeLineItem = (index) => {
        if (lineItems.length > 1) {
            setLineItems(lineItems.filter((_, i) => i !== index));
        }
    };

    const calculateLineTotal = (item) => {
        const subtotal = item.quantity * item.unit_price;
        const tax = subtotal * (item.tax_rate / 100);
        return subtotal + tax;
    };

    const calculateTotals = () => {
        const subtotal = lineItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
        const tax = lineItems.reduce((sum, item) => sum + (item.quantity * item.unit_price * item.tax_rate / 100), 0);
        const total = subtotal + tax;
        return { subtotal, tax, total };
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.invoice_number.trim()) newErrors.invoice_number = 'Invoice number is required';
        if (!formData.partner) newErrors.partner = 'Partner is required';
        if (!formData.invoice_date) newErrors.invoice_date = 'Invoice date is required';
        if (!formData.due_date) newErrors.due_date = 'Due date is required';
        if (lineItems.length === 0) newErrors.items = 'At least one line item is required';
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
            const totals = calculateTotals();
            const invoiceData = {
                ...formData,
                items: lineItems,
                subtotal: totals.subtotal,
                tax_amount: totals.tax,
                total_amount: totals.total,
            };

            if (isEdit) {
                await accountingService.updateInvoice(id, invoiceData);
            } else {
                await accountingService.createInvoice(invoiceData);
            }
            navigate('/accounting/invoices');
        } catch (error) {
            console.error('Error saving invoice:', error);
            setErrors({ submit: 'Failed to save invoice. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const totals = calculateTotals();

    return (
        <div className="invoice-form-page">
            <Card
                title={isEdit ? 'Edit Invoice' : 'New Invoice'}
                subtitle={isEdit ? 'Update invoice details' : 'Create a new sales or purchase invoice'}
            >
                <form onSubmit={handleSubmit} className="invoice-form">
                    {errors.submit && (
                        <div className="form-error-message">{errors.submit}</div>
                    )}

                    <div className="form-section">
                        <h3 className="form-section-title">Invoice Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Invoice Number"
                                name="invoice_number"
                                value={formData.invoice_number}
                                onChange={handleChange}
                                error={errors.invoice_number}
                                required
                                disabled={isEdit}
                            />
                            <Select
                                label="Invoice Type"
                                name="invoice_type"
                                value={formData.invoice_type}
                                onChange={handleChange}
                                options={[
                                    { value: 'sales', label: 'Sales Invoice' },
                                    { value: 'purchase', label: 'Purchase Invoice' },
                                ]}
                                required
                            />
                            <Select
                                label="Partner"
                                name="partner"
                                value={formData.partner}
                                onChange={handleChange}
                                options={partners.map(p => ({ value: p.id, label: p.name }))}
                                error={errors.partner}
                                required
                            />
                            <Input
                                label="Payment Terms"
                                name="payment_terms"
                                value={formData.payment_terms}
                                onChange={handleChange}
                                placeholder="e.g., Net 30"
                            />
                            <Input
                                label="Invoice Date"
                                name="invoice_date"
                                type="date"
                                value={formData.invoice_date}
                                onChange={handleChange}
                                error={errors.invoice_date}
                                required
                            />
                            <Input
                                label="Due Date"
                                name="due_date"
                                type="date"
                                value={formData.due_date}
                                onChange={handleChange}
                                error={errors.due_date}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <div className="line-items-header">
                            <h3 className="form-section-title">Line Items</h3>
                            <Button
                                type="button"
                                variant="primary"
                                size="sm"
                                onClick={addLineItem}
                                icon={
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                }
                            >
                                Add Item
                            </Button>
                        </div>

                        <div className="line-items-table">
                            <div className="line-items-table-header">
                                <div className="line-item-col-product">Product</div>
                                <div className="line-item-col-description">Description</div>
                                <div className="line-item-col-qty">Qty</div>
                                <div className="line-item-col-price">Unit Price</div>
                                <div className="line-item-col-tax">Tax %</div>
                                <div className="line-item-col-total">Total</div>
                                <div className="line-item-col-actions"></div>
                            </div>

                            {lineItems.map((item, index) => (
                                <div key={index} className="line-item-row">
                                    <div className="line-item-col-product">
                                        <Select
                                            name={`product-${index}`}
                                            value={item.product}
                                            onChange={(e) => handleLineItemChange(index, 'product', e.target.value)}
                                            options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))}
                                            placeholder="Select product"
                                        />
                                    </div>
                                    <div className="line-item-col-description">
                                        <Input
                                            name={`description-${index}`}
                                            value={item.description}
                                            onChange={(e) => handleLineItemChange(index, 'description', e.target.value)}
                                            placeholder="Description"
                                        />
                                    </div>
                                    <div className="line-item-col-qty">
                                        <Input
                                            name={`quantity-${index}`}
                                            type="number"
                                            value={item.quantity}
                                            onChange={(e) => handleLineItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                                        />
                                    </div>
                                    <div className="line-item-col-price">
                                        <Input
                                            name={`unit_price-${index}`}
                                            type="number"
                                            step="0.01"
                                            value={item.unit_price}
                                            onChange={(e) => handleLineItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                                        />
                                    </div>
                                    <div className="line-item-col-tax">
                                        <Input
                                            name={`tax_rate-${index}`}
                                            type="number"
                                            step="0.01"
                                            value={item.tax_rate}
                                            onChange={(e) => handleLineItemChange(index, 'tax_rate', parseFloat(e.target.value) || 0)}
                                        />
                                    </div>
                                    <div className="line-item-col-total">
                                        PKR {calculateLineTotal(item).toLocaleString()}
                                    </div>
                                    <div className="line-item-col-actions">
                                        {lineItems.length > 1 && (
                                            <button
                                                type="button"
                                                className="remove-line-item-btn"
                                                onClick={() => removeLineItem(index)}
                                            >
                                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                                    <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                                </svg>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {errors.items && <span className="input-error-text">{errors.items}</span>}
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Totals</h3>
                        <div className="invoice-totals">
                            <div className="invoice-total-row">
                                <span>Subtotal:</span>
                                <strong>PKR {totals.subtotal.toLocaleString()}</strong>
                            </div>
                            <div className="invoice-total-row">
                                <span>Tax:</span>
                                <strong>PKR {totals.tax.toLocaleString()}</strong>
                            </div>
                            <div className="invoice-total-row invoice-grand-total">
                                <span>Total:</span>
                                <strong>PKR {totals.total.toLocaleString()}</strong>
                            </div>
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
                            onClick={() => navigate('/accounting/invoices')}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="primary"
                            loading={loading}
                        >
                            {isEdit ? 'Update Invoice' : 'Create Invoice'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default InvoiceForm;
