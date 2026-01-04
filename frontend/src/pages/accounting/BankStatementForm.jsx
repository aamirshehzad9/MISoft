import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const BankStatementForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        bank_account: '',
        statement_date: new Date().toISOString().split('T')[0],
        opening_balance: '0.00',
        closing_balance: '0.00',
        is_reconciled: false
    });
    const [bankAccounts, setBankAccounts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchBankAccounts();
        if (isEditMode) {
            fetchBankStatement();
        }
    }, [id]);

    const fetchBankAccounts = async () => {
        try {
            const data = await accountingService.getBankAccounts({ is_active: true });
            setBankAccounts(data.results || data);
        } catch (error) {
            console.error('Error fetching bank accounts:', error);
        }
    };

    const fetchBankStatement = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getBankStatementById(id);
            setFormData({
                bank_account: data.bank_account || '',
                statement_date: data.statement_date || '',
                opening_balance: data.opening_balance || '0.00',
                closing_balance: data.closing_balance || '0.00',
                is_reconciled: data.is_reconciled || false
            });
        } catch (error) {
            console.error('Error fetching bank statement:', error);
            alert('Failed to load bank statement');
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

        if (!formData.bank_account) {
            newErrors.bank_account = 'Bank account is required';
        }

        if (!formData.statement_date) {
            newErrors.statement_date = 'Statement date is required';
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
                await accountingService.updateBankStatement(id, formData);
                alert('Bank statement updated successfully');
            } else {
                await accountingService.createBankStatement(formData);
                alert('Bank statement created successfully');
            }
            
            navigate('/dashboard/accounting/bank-statements');
        } catch (error) {
            console.error('Error saving bank statement:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save bank statement');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/bank-statements');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Bank Statement' : 'New Bank Statement'}
                subtitle="Bank Statement Import and Management"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Bank Statement Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="bank_account">
                                    Bank Account <span className="required">*</span>
                                </label>
                                <select
                                    id="bank_account"
                                    name="bank_account"
                                    value={formData.bank_account}
                                    onChange={handleChange}
                                    className={errors.bank_account ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Bank Account</option>
                                    {bankAccounts.map(ba => (
                                        <option key={ba.id} value={ba.id}>
                                            {ba.bank_name} - {ba.account_number}
                                        </option>
                                    ))}
                                </select>
                                {errors.bank_account && <span className="error-message">{errors.bank_account}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="statement_date">
                                    Statement Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="statement_date"
                                    name="statement_date"
                                    type="date"
                                    value={formData.statement_date}
                                    onChange={handleChange}
                                    error={errors.statement_date}
                                    disabled={loading}
                                />
                                {errors.statement_date && <span className="error-message">{errors.statement_date}</span>}
                            </div>
                        </div>

                        <div className="form-row">
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
                            </div>

                            <div className="form-group">
                                <label htmlFor="closing_balance">
                                    Closing Balance
                                </label>
                                <Input
                                    id="closing_balance"
                                    name="closing_balance"
                                    type="number"
                                    step="0.01"
                                    value={formData.closing_balance}
                                    onChange={handleChange}
                                    placeholder="0.00"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_reconciled"
                                        checked={formData.is_reconciled}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Reconciled</span>
                                </label>
                                <small className="help-text">
                                    Mark this statement as reconciled
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Bank Statement' : 'Create Bank Statement')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default BankStatementForm;
