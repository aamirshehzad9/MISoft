import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const TaxCodeForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        code: '',
        description: '',
        tax_percentage: '',
        sales_tax_account: '',
        purchase_tax_account: '',
        is_active: true
    });
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchAccounts();
        if (isEditMode) {
            fetchTaxCode();
        }
    }, [id]);

    const fetchAccounts = async () => {
        try {
            const data = await accountingService.getAccountsV2();
            setAccounts(data.results || data);
        } catch (error) {
            console.error('Error fetching accounts:', error);
        }
    };

    const fetchTaxCode = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getTaxCodeById(id);
            setFormData({
                code: data.code || '',
                description: data.description || '',
                tax_percentage: data.tax_percentage || '',
                sales_tax_account: data.sales_tax_account || '',
                purchase_tax_account: data.purchase_tax_account || '',
                is_active: data.is_active !== undefined ? data.is_active : true
            });
        } catch (error) {
            console.error('Error fetching tax code:', error);
            alert('Failed to load tax code');
        } finally {
            setLoading(false);
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

        if (!formData.code.trim()) {
            newErrors.code = 'Tax code is required';
        }

        if (!formData.description.trim()) {
            newErrors.description = 'Description is required';
        }

        if (!formData.tax_percentage) {
            newErrors.tax_percentage = 'Tax percentage is required';
        } else {
            const percentage = parseFloat(formData.tax_percentage);
            if (isNaN(percentage) || percentage < 0 || percentage > 100) {
                newErrors.tax_percentage = 'Tax percentage must be between 0 and 100';
            }
        }

        if (!formData.sales_tax_account) {
            newErrors.sales_tax_account = 'Sales tax account is required';
        }

        if (!formData.purchase_tax_account) {
            newErrors.purchase_tax_account = 'Purchase tax account is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validate()) {
            return;
        }

        try {
            setLoading(true);
            
            if (isEditMode) {
                await accountingService.updateTaxCode(id, formData);
                alert('Tax code updated successfully');
            } else {
                await accountingService.createTaxCode(formData);
                alert('Tax code created successfully');
            }
            
            navigate('/dashboard/accounting/tax-codes');
        } catch (error) {
            console.error('Error saving tax code:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save tax code');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/tax-codes');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Tax Code' : 'New Tax Code'}
                subtitle="Manage tax rates and codes"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Tax Code Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="code">
                                    Tax Code <span className="required">*</span>
                                </label>
                                <Input
                                    id="code"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    placeholder="e.g., GST18"
                                    error={errors.code}
                                    disabled={loading}
                                />
                                {errors.code && <span className="error-message">{errors.code}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="tax_percentage">
                                    Tax Rate (%) <span className="required">*</span>
                                </label>
                                <Input
                                    id="tax_percentage"
                                    name="tax_percentage"
                                    type="number"
                                    step="0.01"
                                    value={formData.tax_percentage}
                                    onChange={handleChange}
                                    placeholder="e.g., 18.00"
                                    error={errors.tax_percentage}
                                    disabled={loading}
                                />
                                {errors.tax_percentage && <span className="error-message">{errors.tax_percentage}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="description">
                                    Description <span className="required">*</span>
                                </label>
                                <Input
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    placeholder="e.g., Goods and Services Tax 18%"
                                    error={errors.description}
                                    disabled={loading}
                                />
                                {errors.description && <span className="error-message">{errors.description}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="sales_tax_account">
                                    Sales Tax Account <span className="required">*</span>
                                </label>
                                <select
                                    id="sales_tax_account"
                                    name="sales_tax_account"
                                    value={formData.sales_tax_account}
                                    onChange={handleChange}
                                    className={errors.sales_tax_account ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Account</option>
                                    {accounts.map(acc => (
                                        <option key={acc.id} value={acc.id}>
                                            {acc.code} - {acc.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.sales_tax_account && <span className="error-message">{errors.sales_tax_account}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="purchase_tax_account">
                                    Purchase Tax Account <span className="required">*</span>
                                </label>
                                <select
                                    id="purchase_tax_account"
                                    name="purchase_tax_account"
                                    value={formData.purchase_tax_account}
                                    onChange={handleChange}
                                    className={errors.purchase_tax_account ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Account</option>
                                    {accounts.map(acc => (
                                        <option key={acc.id} value={acc.id}>
                                            {acc.code} - {acc.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.purchase_tax_account && <span className="error-message">{errors.purchase_tax_account}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Active</span>
                                </label>
                                <small className="help-text">
                                    Uncheck to deactivate this tax code
                                </small>
                            </div>
                        </div>
                    </div>

                    <div className="form-actions">
                        <Button 
                            type="button" 
                            variant="secondary" 
                            onClick={handleCancel}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button 
                            type="submit" 
                            variant="primary"
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : (isEditMode ? 'Update Tax Code' : 'Create Tax Code')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default TaxCodeForm;
