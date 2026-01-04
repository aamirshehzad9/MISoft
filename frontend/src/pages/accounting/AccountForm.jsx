import React, { useState, useEffect } from 'react';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import Button from '../../components/common/Button';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const AccountForm = ({ account = null, onSuccess, onCancel }) => {
    const isEdit = Boolean(account);
    
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        description: '',
        account_type: 'asset',
        account_group: 'current_asset',
        parent: '',
        is_group: false,
        is_active: true,
    });
    
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});
    
    // Business rules state
    const [hasBalance, setHasBalance] = useState(false);
    const [hasChildren, setHasChildren] = useState(false);

    // Account type options
    const accountTypeOptions = [
        { value: 'asset', label: 'Asset' },
        { value: 'liability', label: 'Liability' },
        { value: 'equity', label: 'Equity' },
        { value: 'revenue', label: 'Revenue' },
        { value: 'expense', label: 'Expense' },
    ];

    // Account group options based on type
    const accountGroupOptions = {
        asset: [
            { value: 'current_asset', label: 'Current Asset' },
            { value: 'fixed_asset', label: 'Fixed Asset' },
            { value: 'investment', label: 'Investment' },
            { value: 'other_asset', label: 'Other Asset' },
        ],
        liability: [
            { value: 'current_liability', label: 'Current Liability' },
            { value: 'long_term_liability', label: 'Long Term Liability' },
            { value: 'other_liability', label: 'Other Liability' },
        ],
        equity: [
            { value: 'capital', label: 'Capital' },
            { value: 'retained_earnings', label: 'Retained Earnings' },
            { value: 'drawings', label: 'Drawings' },
        ],
        revenue: [
            { value: 'sales', label: 'Sales' },
            { value: 'other_income', label: 'Other Income' },
        ],
        expense: [
            { value: 'direct_expense', label: 'Direct Expense' },
            { value: 'indirect_expense', label: 'Indirect Expense' },
            { value: 'operating_expense', label: 'Operating Expense' },
        ],
    };

    useEffect(() => {
        fetchAccounts();
        if (account) {
            setFormData({
                code: account.code || '',
                name: account.name || '',
                description: account.description || '',
                account_type: account.account_type || 'asset',
                account_group: account.account_group || 'current_asset',
                parent: account.parent || '',
                is_group: account.is_group || false,
                is_active: account.is_active !== undefined ? account.is_active : true,
            });
            
            // Check business rules
            const balance = parseFloat(account.current_balance) || 0;
            setHasBalance(balance !== 0);
        }
    }, [account]);

    const fetchAccounts = async () => {
        try {
            const data = await accountingService.getAccountsV2();
            setAccounts(data);
            
            // Check if editing account has children
            if (account) {
                const children = data.filter(acc => acc.parent === account.id);
                setHasChildren(children.length > 0);
            }
        } catch (error) {
            console.error('Error fetching accounts:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        const newValue = type === 'checkbox' ? checked : value;
        
        setFormData(prev => ({
            ...prev,
            [name]: newValue
        }));

        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }

        // Auto-update account_group when account_type changes
        if (name === 'account_type') {
            const firstGroup = accountGroupOptions[value][0].value;
            setFormData(prev => ({
                ...prev,
                account_group: firstGroup
            }));
        }
    };

    const validate = () => {
        const newErrors = {};
        
        if (!formData.code.trim()) {
            newErrors.code = 'Account code is required';
        }
        
        if (!formData.name.trim()) {
            newErrors.name = 'Account name is required';
        }
        
        if (!formData.account_type) {
            newErrors.account_type = 'Account type is required';
        }
        
        if (!formData.account_group) {
            newErrors.account_group = 'Account group is required';
        }

        // Validate parent account (no circular reference)
        if (formData.parent && isEdit && formData.parent === account.id) {
            newErrors.parent = 'Account cannot be its own parent';
        }

        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const newErrors = validate();
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }
        
        // Confirmation dialogs for critical changes
        if (isEdit && formData.parent !== account.parent && formData.parent) {
            const confirmed = window.confirm(
                'Changing parent account will affect hierarchy. Continue?'
            );
            if (!confirmed) return;
        }
        
        if (isEdit && formData.is_active === false && account.is_active === true) {
            const confirmed = window.confirm(
                'Deactivating this account will hide it from dropdowns. Continue?'
            );
            if (!confirmed) return;
        }

        try {
            setLoading(true);
            
            // Prepare data
            const submitData = {
                ...formData,
                parent: formData.parent || null,
            };

            if (isEdit) {
                await accountingService.updateAccount(account.id, submitData);
            } else {
                await accountingService.createAccount(submitData);
            }

            onSuccess();
        } catch (error) {
            console.error('Error saving account:', error);
            if (error.response?.data) {
                // Handle backend validation errors
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key])
                        ? error.response.data[key][0]
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                setErrors({ submit: 'Failed to save account. Please try again.' });
            }
        } finally {
            setLoading(false);
        }
    };

    // Filter parent accounts (only group accounts)
    const parentAccountOptions = accounts
        .filter(acc => acc.is_group && (!isEdit || acc.id !== account?.id))
        .map(acc => ({
            value: acc.id,
            label: `${acc.code} - ${acc.name}`
        }));

    return (
        <form onSubmit={handleSubmit} className="account-form">
            {errors.submit && (
                <div className="form-error-message">{errors.submit}</div>
            )}

            <div className="form-section">
                <h4 className="form-section-title">Basic Information</h4>
                <div className="form-grid">
                    <Input
                        label="Account Code"
                        name="code"
                        value={formData.code}
                        onChange={handleChange}
                        error={errors.code}
                        required
                        disabled={isEdit}
                        helperText={isEdit ? "Code cannot be changed" : "Unique identifier"}
                    />
                    
                    <Input
                        label="Account Name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        error={errors.name}
                        required
                    />
                </div>

                <Input
                    label="Description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    error={errors.description}
                />
            </div>

            <div className="form-section">
                <h4 className="form-section-title">Classification</h4>
                <div className="form-grid">
                    <Select
                        label="Account Type"
                        name="account_type"
                        value={formData.account_type}
                        onChange={handleChange}
                        options={accountTypeOptions}
                        error={errors.account_type}
                        required
                        disabled={isEdit && hasBalance}
                        helperText={isEdit && hasBalance ? "⚠️ Cannot change type - Account has balance" : ""}
                    />

                    <Select
                        label="Account Group"
                        name="account_group"
                        value={formData.account_group}
                        onChange={handleChange}
                        options={accountGroupOptions[formData.account_type] || []}
                        error={errors.account_group}
                        required
                        disabled={isEdit && hasBalance}
                        helperText={isEdit && hasBalance ? "⚠️ Cannot change group - Account has balance" : ""}
                    />
                </div>

                <Select
                    label="Parent Account"
                    name="parent"
                    value={formData.parent}
                    onChange={handleChange}
                    options={parentAccountOptions}
                    error={errors.parent}
                    placeholder="Select parent account (optional)"
                />
            </div>

            <div className="form-section">
                <h4 className="form-section-title">Settings</h4>
                <div className="checkbox-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="is_group"
                            checked={formData.is_group}
                            onChange={handleChange}
                            disabled={isEdit && (hasBalance || hasChildren)}
                        />
                        <span>Group Account (cannot have direct postings)</span>
                        {isEdit && hasBalance && <span className="field-warning"> - Cannot change (has balance)</span>}
                        {isEdit && hasChildren && <span className="field-warning"> - Cannot change (has children)</span>}
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
                    onClick={onCancel}
                    disabled={loading}
                >
                    Cancel
                </Button>
                <Button
                    type="submit"
                    variant="primary"
                    loading={loading}
                >
                    {isEdit ? 'Update Account' : 'Create Account'}
                </Button>
            </div>
        </form>
    );
};

export default AccountForm;
