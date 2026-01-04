import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const CurrencyForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        currency_code: '',
        currency_name: '',
        symbol: '',
        is_base_currency: false,
        is_active: true
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (isEditMode) {
            fetchCurrency();
        }
    }, [id]);

    const fetchCurrency = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getCurrencyById(id);
            setFormData({
                currency_code: data.currency_code || '',
                currency_name: data.currency_name || '',
                symbol: data.symbol || '',
                is_base_currency: data.is_base_currency || false,
                is_active: data.is_active !== undefined ? data.is_active : true
            });
        } catch (error) {
            console.error('Error fetching currency:', error);
            alert('Failed to load currency');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        let processedValue = type === 'checkbox' ? checked : value;
        
        // Auto-uppercase currency code
        if (name === 'currency_code') {
            processedValue = value.toUpperCase();
        }
        
        setFormData(prev => ({
            ...prev,
            [name]: processedValue
        }));
        
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.currency_code.trim()) {
            newErrors.currency_code = 'Currency code is required';
        } else if (formData.currency_code.length !== 3) {
            newErrors.currency_code = 'Currency code must be exactly 3 characters (e.g., USD, EUR, PKR)';
        }

        if (!formData.currency_name.trim()) {
            newErrors.currency_name = 'Currency name is required';
        }

        if (!formData.symbol.trim()) {
            newErrors.symbol = 'Currency symbol is required';
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
                await accountingService.updateCurrency(id, formData);
                alert('Currency updated successfully');
            } else {
                await accountingService.createCurrency(formData);
                alert('Currency created successfully');
            }
            
            navigate('/dashboard/accounting/currencies');
        } catch (error) {
            console.error('Error saving currency:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save currency');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/currencies');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Currency' : 'New Currency'}
                subtitle="IAS 21 Compliant Currency Management"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Currency Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="currency_code">
                                    Currency Code <span className="required">*</span>
                                </label>
                                <Input
                                    id="currency_code"
                                    name="currency_code"
                                    value={formData.currency_code}
                                    onChange={handleChange}
                                    placeholder="e.g., USD, EUR, PKR"
                                    maxLength="3"
                                    error={errors.currency_code}
                                    disabled={loading}
                                />
                                {errors.currency_code && <span className="error-message">{errors.currency_code}</span>}
                                <small className="help-text">3-character ISO 4217 code</small>
                            </div>

                            <div className="form-group">
                                <label htmlFor="symbol">
                                    Symbol <span className="required">*</span>
                                </label>
                                <Input
                                    id="symbol"
                                    name="symbol"
                                    value={formData.symbol}
                                    onChange={handleChange}
                                    placeholder="e.g., $, €, ₨"
                                    error={errors.symbol}
                                    disabled={loading}
                                />
                                {errors.symbol && <span className="error-message">{errors.symbol}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="currency_name">
                                    Currency Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="currency_name"
                                    name="currency_name"
                                    value={formData.currency_name}
                                    onChange={handleChange}
                                    placeholder="e.g., US Dollar, Euro, Pakistani Rupee"
                                    error={errors.currency_name}
                                    disabled={loading}
                                />
                                {errors.currency_name && <span className="error-message">{errors.currency_name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_base_currency"
                                        checked={formData.is_base_currency}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Base Currency</span>
                                </label>
                                <small className="help-text">
                                    Mark this as the base currency for exchange rate calculations (IAS 21)
                                </small>
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
                                    Uncheck to deactivate this currency
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Currency' : 'Create Currency')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default CurrencyForm;
