import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const ExchangeRateForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        from_currency: '',
        to_currency: '',
        rate_date: new Date().toISOString().split('T')[0],
        exchange_rate: ''
    });
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchCurrencies();
        if (isEditMode) {
            fetchExchangeRate();
        }
    }, [id]);

    const fetchCurrencies = async () => {
        try {
            const data = await accountingService.getCurrencies({ is_active: true });
            setCurrencies(data.results || data);
        } catch (error) {
            console.error('Error fetching currencies:', error);
        }
    };

    const fetchExchangeRate = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getExchangeRateById(id);
            setFormData({
                from_currency: data.from_currency || '',
                to_currency: data.to_currency || '',
                rate_date: data.rate_date || '',
                exchange_rate: data.exchange_rate || ''
            });
        } catch (error) {
            console.error('Error fetching exchange rate:', error);
            alert('Failed to load exchange rate');
        } finally {
            setLoading(false);
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

        if (!formData.from_currency) {
            newErrors.from_currency = 'From currency is required';
        }

        if (!formData.to_currency) {
            newErrors.to_currency = 'To currency is required';
        }

        if (formData.from_currency && formData.to_currency && formData.from_currency === formData.to_currency) {
            newErrors.to_currency = 'To currency must be different from From currency';
        }

        if (!formData.rate_date) {
            newErrors.rate_date = 'Rate date is required';
        }

        if (!formData.exchange_rate) {
            newErrors.exchange_rate = 'Exchange rate is required';
        } else {
            const rate = parseFloat(formData.exchange_rate);
            if (isNaN(rate) || rate <= 0) {
                newErrors.exchange_rate = 'Exchange rate must be greater than 0';
            }
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
                await accountingService.updateExchangeRate(id, formData);
                alert('Exchange rate updated successfully');
            } else {
                await accountingService.createExchangeRate(formData);
                alert('Exchange rate created successfully');
            }
            
            navigate('/dashboard/accounting/exchange-rates');
        } catch (error) {
            console.error('Error saving exchange rate:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save exchange rate');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/exchange-rates');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Exchange Rate' : 'New Exchange Rate'}
                subtitle="IAS 21 Compliant Exchange Rate Management"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Exchange Rate Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="from_currency">
                                    From Currency <span className="required">*</span>
                                </label>
                                <select
                                    id="from_currency"
                                    name="from_currency"
                                    value={formData.from_currency}
                                    onChange={handleChange}
                                    className={errors.from_currency ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Currency</option>
                                    {currencies.map(curr => (
                                        <option key={curr.id} value={curr.id}>
                                            {curr.currency_code} - {curr.currency_name}
                                        </option>
                                    ))}
                                </select>
                                {errors.from_currency && <span className="error-message">{errors.from_currency}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="to_currency">
                                    To Currency <span className="required">*</span>
                                </label>
                                <select
                                    id="to_currency"
                                    name="to_currency"
                                    value={formData.to_currency}
                                    onChange={handleChange}
                                    className={errors.to_currency ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Currency</option>
                                    {currencies.map(curr => (
                                        <option key={curr.id} value={curr.id}>
                                            {curr.currency_code} - {curr.currency_name}
                                        </option>
                                    ))}
                                </select>
                                {errors.to_currency && <span className="error-message">{errors.to_currency}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="rate_date">
                                    Rate Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="rate_date"
                                    name="rate_date"
                                    type="date"
                                    value={formData.rate_date}
                                    onChange={handleChange}
                                    error={errors.rate_date}
                                    disabled={loading}
                                />
                                {errors.rate_date && <span className="error-message">{errors.rate_date}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="exchange_rate">
                                    Exchange Rate <span className="required">*</span>
                                </label>
                                <Input
                                    id="exchange_rate"
                                    name="exchange_rate"
                                    type="number"
                                    step="0.0001"
                                    value={formData.exchange_rate}
                                    onChange={handleChange}
                                    placeholder="e.g., 1.2345"
                                    error={errors.exchange_rate}
                                    disabled={loading}
                                />
                                {errors.exchange_rate && <span className="error-message">{errors.exchange_rate}</span>}
                                <small className="help-text">4 decimal places precision (IAS 21)</small>
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Exchange Rate' : 'Create Exchange Rate')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default ExchangeRateForm;
