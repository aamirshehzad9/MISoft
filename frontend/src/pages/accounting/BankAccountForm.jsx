import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const BankAccountForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        account_number: '',
        account_name: '',
        bank_name: '',
        branch: '',
        currency: '',
        opening_balance: '0.00',
        is_active: true
    });
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchCurrencies();
        if (isEditMode) {
            fetchBankAccount();
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

    const fetchBankAccount = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getBankAccountById(id);
            setFormData({
                account_number: data.account_number || '',
                account_name: data.account_name || '',
                bank_name: data.bank_name || '',
                branch: data.branch || '',
                currency: data.currency || '',
                opening_balance: data.opening_balance || '0.00',
                is_active: data.is_active !== undefined ? data.is_active : true
            });
        } catch (error) {
            console.error('Error fetching bank account:', error);
            alert('Failed to load bank account');
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

        if (!formData.account_number.trim()) {
            newErrors.account_number = 'Account number is required';
        }

        if (!formData.account_name.trim()) {
            newErrors.account_name = 'Account name is required';
        }

        if (!formData.bank_name.trim()) {
            newErrors.bank_name = 'Bank name is required';
        }

        if (!formData.currency) {
            newErrors.currency = 'Currency is required';
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
                await accountingService.updateBankAccount(id, formData);
                alert('Bank account updated successfully');
            } else {
                await accountingService.createBankAccount(formData);
                alert('Bank account created successfully');
            }
            
            navigate('/dashboard/accounting/bank-accounts');
        } catch (error) {
            console.error('Error saving bank account:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save bank account');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/bank-accounts');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Bank Account' : 'New Bank Account'}
                subtitle="Banking Operations Management"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Bank Account Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="account_number">
                                    Account Number <span className="required">*</span>
                                </label>
                                <Input
                                    id="account_number"
                                    name="account_number"
                                    value={formData.account_number}
                                    onChange={handleChange}
                                    placeholder="e.g., 1234567890"
                                    error={errors.account_number}
                                    disabled={loading}
                                />
                                {errors.account_number && <span className="error-message">{errors.account_number}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="account_name">
                                    Account Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="account_name"
                                    name="account_name"
                                    value={formData.account_name}
                                    onChange={handleChange}
                                    placeholder="e.g., Company Main Account"
                                    error={errors.account_name}
                                    disabled={loading}
                                />
                                {errors.account_name && <span className="error-message">{errors.account_name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="bank_name">
                                    Bank Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="bank_name"
                                    name="bank_name"
                                    value={formData.bank_name}
                                    onChange={handleChange}
                                    placeholder="e.g., ABC Bank"
                                    error={errors.bank_name}
                                    disabled={loading}
                                />
                                {errors.bank_name && <span className="error-message">{errors.bank_name}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="branch">
                                    Branch
                                </label>
                                <Input
                                    id="branch"
                                    name="branch"
                                    value={formData.branch}
                                    onChange={handleChange}
                                    placeholder="e.g., Main Branch"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="currency">
                                    Currency <span className="required">*</span>
                                </label>
                                <select
                                    id="currency"
                                    name="currency"
                                    value={formData.currency}
                                    onChange={handleChange}
                                    className={errors.currency ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Currency</option>
                                    {currencies.map(curr => (
                                        <option key={curr.id} value={curr.id}>
                                            {curr.currency_code} - {curr.currency_name}
                                        </option>
                                    ))}
                                </select>
                                {errors.currency && <span className="error-message">{errors.currency}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="opening_balance">
                                    Opening Balance
                                </label>
                                <Input
                                    id="opening_balance"
                                    name="opening_balance"
                                    type="number"
                                    step="0.01"
                                    value={formData.opening_balance}
                                    onChange={handleChange}
                                    placeholder="0.00"
                                    disabled={loading}
                                />
                                <small className="help-text">Initial balance for this account</small>
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
                                    Uncheck to deactivate this bank account
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Bank Account' : 'Create Bank Account')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default BankAccountForm;
