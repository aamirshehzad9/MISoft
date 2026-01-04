import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const TaxMasterForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        tax_code: '',
        tax_name: '',
        tax_type: '',
        tax_rate: '',
        tax_collected_account: '',
        tax_paid_account: '',
        is_active: true
    });
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    const taxTypes = [
        { value: 'vat', label: 'VAT' },
        { value: 'gst', label: 'GST' },
        { value: 'sales_tax', label: 'Sales Tax' },
        { value: 'service_tax', label: 'Service Tax' },
        { value: 'excise', label: 'Excise Duty' },
        { value: 'customs', label: 'Customs Duty' },
    ];

    useEffect(() => {
        fetchAccounts();
        if (isEditMode) {
            fetchTaxMaster();
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

    const fetchTaxMaster = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getTaxMasterById(id);
            setFormData({
                tax_code: data.tax_code || '',
                tax_name: data.tax_name || '',
                tax_type: data.tax_type || '',
                tax_rate: data.tax_rate || '',
                tax_collected_account: data.tax_collected_account || '',
                tax_paid_account: data.tax_paid_account || '',
                is_active: data.is_active !== undefined ? data.is_active : true
            });
        } catch (error) {
            console.error('Error fetching tax master:', error);
            alert('Failed to load tax master');
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

        if (!formData.tax_code.trim()) {
            newErrors.tax_code = 'Tax code is required';
        }

        if (!formData.tax_name.trim()) {
            newErrors.tax_name = 'Tax name is required';
        }

        if (!formData.tax_type) {
            newErrors.tax_type = 'Tax type is required';
        }

        if (!formData.tax_rate) {
            newErrors.tax_rate = 'Tax rate is required';
        } else {
            const rate = parseFloat(formData.tax_rate);
            if (isNaN(rate) || rate < 0 || rate > 100) {
                newErrors.tax_rate = 'Tax rate must be between 0 and 100';
            }
        }

        if (!formData.tax_collected_account) {
            newErrors.tax_collected_account = 'Tax collected account is required';
        }

        if (!formData.tax_paid_account) {
            newErrors.tax_paid_account = 'Tax paid account is required';
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
                await accountingService.updateTaxMaster(id, formData);
                alert('Tax master updated successfully');
            } else {
                await accountingService.createTaxMaster(formData);
                alert('Tax master created successfully');
            }
            
            navigate('/dashboard/accounting/tax-masters');
        } catch (error) {
            console.error('Error saving tax master:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save tax master');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/tax-masters');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Tax Master' : 'New Tax Master'}
                subtitle="IAS 12 Compliant Tax Management"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Tax Master Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="tax_code">
                                    Tax Code <span className="required">*</span>
                                </label>
                                <Input
                                    id="tax_code"
                                    name="tax_code"
                                    value={formData.tax_code}
                                    onChange={handleChange}
                                    placeholder="e.g., GST18"
                                    error={errors.tax_code}
                                    disabled={loading}
                                />
                                {errors.tax_code && <span className="error-message">{errors.tax_code}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="tax_name">
                                    Tax Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="tax_name"
                                    name="tax_name"
                                    value={formData.tax_name}
                                    onChange={handleChange}
                                    placeholder="e.g., Goods and Services Tax 18%"
                                    error={errors.tax_name}
                                    disabled={loading}
                                />
                                {errors.tax_name && <span className="error-message">{errors.tax_name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="tax_type">
                                    Tax Type <span className="required">*</span>
                                </label>
                                <select
                                    id="tax_type"
                                    name="tax_type"
                                    value={formData.tax_type}
                                    onChange={handleChange}
                                    className={errors.tax_type ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Tax Type</option>
                                    {taxTypes.map(type => (
                                        <option key={type.value} value={type.value}>
                                            {type.label}
                                        </option>
                                    ))}
                                </select>
                                {errors.tax_type && <span className="error-message">{errors.tax_type}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="tax_rate">
                                    Tax Rate (%) <span className="required">*</span>
                                </label>
                                <Input
                                    id="tax_rate"
                                    name="tax_rate"
                                    type="number"
                                    step="0.01"
                                    value={formData.tax_rate}
                                    onChange={handleChange}
                                    placeholder="e.g., 18.00"
                                    error={errors.tax_rate}
                                    disabled={loading}
                                />
                                {errors.tax_rate && <span className="error-message">{errors.tax_rate}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="tax_collected_account">
                                    Tax Collected Account <span className="required">*</span>
                                </label>
                                <select
                                    id="tax_collected_account"
                                    name="tax_collected_account"
                                    value={formData.tax_collected_account}
                                    onChange={handleChange}
                                    className={errors.tax_collected_account ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Account</option>
                                    {accounts.map(acc => (
                                        <option key={acc.id} value={acc.id}>
                                            {acc.code} - {acc.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.tax_collected_account && <span className="error-message">{errors.tax_collected_account}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="tax_paid_account">
                                    Tax Paid Account <span className="required">*</span>
                                </label>
                                <select
                                    id="tax_paid_account"
                                    name="tax_paid_account"
                                    value={formData.tax_paid_account}
                                    onChange={handleChange}
                                    className={errors.tax_paid_account ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Account</option>
                                    {accounts.map(acc => (
                                        <option key={acc.id} value={acc.id}>
                                            {acc.code} - {acc.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.tax_paid_account && <span className="error-message">{errors.tax_paid_account}</span>}
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
                                    Uncheck to deactivate this tax master
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Tax Master' : 'Create Tax Master')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default TaxMasterForm;
