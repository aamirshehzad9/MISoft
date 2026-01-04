import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import accountingService from '../../services/accounting';
import ReferenceEditor from './ReferenceEditor';
import './InvoiceForm.css'; // Reusing styles

const VoucherForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const [searchParams] = useSearchParams();
    const isEdit = Boolean(id);
    const initialType = searchParams.get('type') || 'JE';

    const [loading, setLoading] = useState(false);
    const [accounts, setAccounts] = useState([]);
    const [formData, setFormData] = useState({
        voucher_number: '',
        voucher_type: initialType,
        voucher_date: new Date().toISOString().split('T')[0],
        reference_number: '',
        narration: '',
        user_references: {},
        status: 'draft',
    });
    const [entries, setEntries] = useState([
        { account_id: '', debit: 0, credit: 0, description: '' },
        { account_id: '', debit: 0, credit: 0, description: '' }
    ]);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchAccounts();
        if (isEdit) {
            fetchVoucher();
        } else {
            generateVoucherNumber(initialType);
        }
    }, [id]);

    const fetchVoucher = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getVoucherById(id);
            setFormData({
                voucher_number: data.voucher_number,
                voucher_type: data.voucher_type,
                voucher_date: data.voucher_date,
                reference_number: data.reference_number || '',
                narration: data.narration || '',
                user_references: data.user_references || {},
                status: data.status,
            });
            if (data.entries && data.entries.length > 0) {
                setEntries(data.entries.map(e => ({
                    account_id: e.account,
                    debit: e.debit_amount,
                    credit: e.credit_amount,
                    description: e.description || ''
                })));
            }
        } catch (error) {
            console.error('Error fetching voucher:', error);
        } finally {
            setLoading(false);
        }
    };

    const handlePost = async () => {
        if (!window.confirm('Are you sure you want to post this voucher? This action cannot be undone.')) return;
        try {
            setLoading(true);
            await accountingService.postVoucher(id);
            fetchVoucher();
        } catch (error) {
            console.error('Error posting voucher:', error);
            setErrors({ submit: 'Failed to post voucher.' });
        } finally {
            setLoading(false);
        }
    };

    const generateVoucherNumber = async (type) => {
        try {
            // Map voucher type to document type for numbering scheme
            const docTypeMapping = {
                'JE': 'journal',
                'SI': 'invoice',
                'PI': 'purchase_order',
                'CPV': 'payment',
                'BPV': 'payment',
                'CRV': 'receipt',
                'BRV': 'receipt',
                'DN': 'debit_note',
                'CN': 'credit_note',
                'CE': 'journal',
            };
            
            const document_type = docTypeMapping[type] || 'voucher';
            const response = await accountingService.previewNumber({ document_type });
            
            if (response && response.preview) {
                setFormData(prev => ({ ...prev, voucher_number: response.preview }));
            }
        } catch (error) {
            // Fallback to timestamp if no scheme exists or error
            console.log('Using fallback numbering:', error);
            const timestamp = Date.now();
            const num = `${type}-${timestamp.toString().slice(-8)}`;
            setFormData(prev => ({ ...prev, voucher_number: num }));
        }
    };

    const fetchAccounts = async () => {
        try {
            const data = await accountingService.getAccountsV2();
            setAccounts(data);
        } catch (error) {
            console.error('Error fetching accounts:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));

        if (name === 'voucher_type' && !isEdit) {
            generateVoucherNumber(value);
        }
    };

    const handleEntryChange = (index, field, value) => {
        const newEntries = [...entries];
        newEntries[index][field] = value;
        setEntries(newEntries);
    };

    const addEntry = () => {
        setEntries([...entries, { account_id: '', debit: 0, credit: 0, description: '' }]);
    };

    const removeEntry = (index) => {
        if (entries.length > 2) {
            setEntries(entries.filter((_, i) => i !== index));
        }
    };

    const calculateTotals = () => {
        const totalDebit = entries.reduce((sum, item) => sum + (parseFloat(item.debit) || 0), 0);
        const totalCredit = entries.reduce((sum, item) => sum + (parseFloat(item.credit) || 0), 0);
        return { totalDebit, totalCredit, difference: totalDebit - totalCredit };
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.voucher_number) newErrors.voucher_number = 'Voucher number is required';
        if (!formData.voucher_date) newErrors.voucher_date = 'Date is required';

        const { totalDebit, totalCredit } = calculateTotals();
        if (Math.abs(totalDebit - totalCredit) > 0.01) {
            newErrors.entries = `Entries are not balanced. Difference: ${Math.abs(totalDebit - totalCredit).toFixed(2)}`;
        }

        entries.forEach((entry, index) => {
            if (!entry.account_id) newErrors[`account_${index}`] = 'Account is required';
        });

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
            const payload = {
                ...formData,
                total_amount: calculateTotals().totalDebit,
                entries: entries.map(e => ({
                    account_id: e.account_id,
                    debit: parseFloat(e.debit) || 0,
                    credit: parseFloat(e.credit) || 0,
                    description: e.description
                }))
            };

            await accountingService.createVoucher(payload);
            navigate('/dashboard/accounting/vouchers');
        } catch (error) {
            console.error('Error saving voucher:', error);
            setErrors({ submit: 'Failed to save voucher.' });
        } finally {
            setLoading(false);
        }
    };

    const { totalDebit, totalCredit, difference } = calculateTotals();

    const voucherTypes = [
        { value: 'JE', label: 'Journal Entry' },
        { value: 'CPV', label: 'Cash Payment Voucher' },
        { value: 'BPV', label: 'Bank Payment Voucher' },
        { value: 'CRV', label: 'Cash Receipt Voucher' },
        { value: 'BRV', label: 'Bank Receipt Voucher' },
        { value: 'DN', label: 'Debit Note' },
        { value: 'CN', label: 'Credit Note' },
        { value: 'CE', label: 'Contra Entry' },
    ];

    const getTitle = () => {
        const type = voucherTypes.find(t => t.value === formData.voucher_type);
        return isEdit ? `Edit ${type?.label || 'Voucher'}` : `New ${type?.label || 'Voucher'}`;
    };

    return (
        <div className="invoice-form-page">
            <Card title={getTitle()} subtitle="Manage financial transaction">
                <form onSubmit={handleSubmit} className="invoice-form">
                    {errors.submit && <div className="form-error-message">{errors.submit}</div>}
                    {errors.entries && <div className="form-error-message">{errors.entries}</div>}

                    <div className="form-section">
                        <div className="form-grid">
                            <Select
                                label="Voucher Type"
                                name="voucher_type"
                                value={formData.voucher_type}
                                onChange={handleChange}
                                options={voucherTypes}
                                disabled={isEdit}
                            />
                            <Input label="Voucher Number" name="voucher_number" value={formData.voucher_number} onChange={handleChange} required />
                            <Input label="Date" name="voucher_date" type="date" value={formData.voucher_date} onChange={handleChange} required />
                            <Input label="Reference" name="reference_number" value={formData.reference_number} onChange={handleChange} />
                            <Input label="Narration" name="narration" value={formData.narration} onChange={handleChange} className="form-grid-full" />
                        </div>
                        <ReferenceEditor 
                            modelName="voucher" 
                            value={formData.user_references} 
                            onChange={(refs) => setFormData(prev => ({ ...prev, user_references: refs }))}
                            readOnly={formData.status === 'posted' || formData.status === 'cancelled'}
                        />
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Entries</h3>
                        <div className="line-items-table">
                            <div className="line-items-table-header" style={{ gridTemplateColumns: '2fr 2fr 1fr 1fr 50px' }}>
                                <div>Account</div>
                                <div>Description</div>
                                <div>Debit</div>
                                <div>Credit</div>
                                <div></div>
                            </div>
                            {entries.map((entry, index) => (
                                <div key={index} className="line-item-row" style={{ gridTemplateColumns: '2fr 2fr 1fr 1fr 50px' }}>
                                    <Select
                                        value={entry.account_id}
                                        onChange={(e) => handleEntryChange(index, 'account_id', e.target.value)}
                                        options={accounts.filter(a => !a.is_group).map(a => ({ value: a.id, label: `${a.code} - ${a.name}` }))}
                                        placeholder="Select Account"
                                        error={errors[`account_${index}`]}
                                    />
                                    <Input
                                        value={entry.description}
                                        onChange={(e) => handleEntryChange(index, 'description', e.target.value)}
                                        placeholder="Line description"
                                    />
                                    <Input
                                        type="number"
                                        value={entry.debit}
                                        onChange={(e) => handleEntryChange(index, 'debit', e.target.value)}
                                        disabled={parseFloat(entry.credit) > 0}
                                    />
                                    <Input
                                        type="number"
                                        value={entry.credit}
                                        onChange={(e) => handleEntryChange(index, 'credit', e.target.value)}
                                        disabled={parseFloat(entry.debit) > 0}
                                    />
                                    <button type="button" onClick={() => removeEntry(index)} className="remove-line-item-btn">×</button>
                                </div>
                            ))}
                        </div>
                        <Button type="button" size="sm" onClick={addEntry}>Add Line</Button>
                    </div>

                    <div className="form-section">
                        <div className="invoice-totals">
                            <div className="invoice-total-row"><span>Total Debit:</span><strong>{totalDebit.toFixed(2)}</strong></div>
                            <div className="invoice-total-row"><span>Total Credit:</span><strong>{totalCredit.toFixed(2)}</strong></div>
                            <div className={`invoice-total-row ${difference !== 0 ? 'text-danger' : 'text-success'}`}>
                                <span>Difference:</span><strong>{difference.toFixed(2)}</strong>
                            </div>
                        </div>
                    </div>

                    <div className="form-actions">
                        <Button type="button" variant="secondary" onClick={() => navigate('/dashboard/accounting/vouchers')}>Cancel</Button>
                        {formData.status === 'draft' && (
                            <>
                                <Button type="submit" variant="primary" loading={loading} disabled={difference !== 0}>Save Draft</Button>
                                {isEdit && (
                                    <Button type="button" variant="success" loading={loading} onClick={handlePost} disabled={difference !== 0}>Post</Button>
                                )}
                            </>
                        )}
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default VoucherForm;
