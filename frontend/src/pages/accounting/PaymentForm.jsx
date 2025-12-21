import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import accountingService from '../../services/accounting';
import partnersService from '../../services/partners';
import './PaymentForm.css';

const PaymentForm = () => {
    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);
    const [partners, setPartners] = useState([]);
    const [bankAccounts, setBankAccounts] = useState([]);
    const [invoices, setInvoices] = useState([]);
    const [formData, setFormData] = useState({
        payment_number: '',
        payment_type: 'receipt',
        payment_mode: 'bank_transfer',
        partner: '',
        bank_account: '',
        amount: 0,
        payment_date: new Date().toISOString().split('T')[0],
        reference: '',
        notes: '',
    });
    const [selectedInvoices, setSelectedInvoices] = useState([]);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchPartners();
        fetchBankAccounts();
        generatePaymentNumber();
    }, []);

    useEffect(() => {
        if (formData.partner) {
            fetchPartnerInvoices();
        }
    }, [formData.partner, formData.payment_type]);

    const generatePaymentNumber = () => {
        const timestamp = Date.now();
        const paymentNum = `PAY-${timestamp.toString().slice(-8)}`;
        setFormData(prev => ({ ...prev, payment_number: paymentNum }));
    };

    const fetchPartners = async () => {
        try {
            const data = await partnersService.getAll();
            setPartners(data);
        } catch (error) {
            console.error('Error fetching partners:', error);
        }
    };

    const fetchBankAccounts = async () => {
        try {
            const data = await accountingService.getBankAccounts();
            setBankAccounts(data || []);
        } catch (error) {
            console.error('Error fetching bank accounts:', error);
        }
    };

    const fetchPartnerInvoices = async () => {
        try {
            // Fetch invoices for the selected partner
            const allInvoices = formData.payment_type === 'receipt'
                ? await accountingService.getSalesInvoices()
                : await accountingService.getPurchaseInvoices();

            const partnerInvoices = allInvoices.filter(inv =>
                inv.partner === parseInt(formData.partner) &&
                inv.status !== 'paid' &&
                parseFloat(inv.outstanding_amount || 0) > 0
            );
            setInvoices(partnerInvoices);
        } catch (error) {
            console.error('Error fetching invoices:', error);
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

    const handleInvoiceAllocation = (invoiceId, amount) => {
        const newAllocations = [...selectedInvoices];
        const existingIndex = newAllocations.findIndex(a => a.invoice === invoiceId);

        if (existingIndex >= 0) {
            if (amount > 0) {
                newAllocations[existingIndex].amount = amount;
            } else {
                newAllocations.splice(existingIndex, 1);
            }
        } else if (amount > 0) {
            newAllocations.push({ invoice: invoiceId, amount });
        }

        setSelectedInvoices(newAllocations);

        // Update total payment amount
        const totalAllocated = newAllocations.reduce((sum, a) => sum + parseFloat(a.amount || 0), 0);
        setFormData(prev => ({ ...prev, amount: totalAllocated }));
    };

    const getAllocatedAmount = (invoiceId) => {
        const allocation = selectedInvoices.find(a => a.invoice === invoiceId);
        return allocation ? allocation.amount : 0;
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.payment_number.trim()) newErrors.payment_number = 'Payment number is required';
        if (!formData.partner) newErrors.partner = 'Partner is required';
        if (!formData.amount || formData.amount <= 0) newErrors.amount = 'Amount must be greater than 0';
        if (!formData.payment_date) newErrors.payment_date = 'Payment date is required';
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
            const paymentData = {
                ...formData,
                allocations: selectedInvoices,
            };

            await accountingService.createPayment(paymentData);
            navigate('/accounting/payments');
        } catch (error) {
            console.error('Error saving payment:', error);
            setErrors({ submit: 'Failed to save payment. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const paymentModeOptions = [
        { value: 'cash', label: 'Cash' },
        { value: 'bank_transfer', label: 'Bank Transfer' },
        { value: 'cheque', label: 'Cheque' },
        { value: 'credit_card', label: 'Credit Card' },
        { value: 'debit_card', label: 'Debit Card' },
    ];

    return (
        <div className="payment-form-page">
            <Card
                title="New Payment"
                subtitle="Record a payment receipt or payment made"
            >
                <form onSubmit={handleSubmit} className="payment-form">
                    {errors.submit && (
                        <div className="form-error-message">{errors.submit}</div>
                    )}

                    <div className="form-section">
                        <h3 className="form-section-title">Payment Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Payment Number"
                                name="payment_number"
                                value={formData.payment_number}
                                onChange={handleChange}
                                error={errors.payment_number}
                                required
                                disabled
                            />
                            <Select
                                label="Payment Type"
                                name="payment_type"
                                value={formData.payment_type}
                                onChange={handleChange}
                                options={[
                                    { value: 'receipt', label: 'Payment Receipt (Customer)' },
                                    { value: 'payment', label: 'Payment Made (Vendor)' },
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
                                label="Payment Date"
                                name="payment_date"
                                type="date"
                                value={formData.payment_date}
                                onChange={handleChange}
                                error={errors.payment_date}
                                required
                            />
                            <Select
                                label="Payment Mode"
                                name="payment_mode"
                                value={formData.payment_mode}
                                onChange={handleChange}
                                options={paymentModeOptions}
                                required
                            />
                            <Select
                                label="Bank Account"
                                name="bank_account"
                                value={formData.bank_account}
                                onChange={handleChange}
                                options={bankAccounts.map(ba => ({ value: ba.id, label: ba.account_name }))}
                                placeholder="Select bank account"
                            />
                            <Input
                                label="Reference"
                                name="reference"
                                value={formData.reference}
                                onChange={handleChange}
                                placeholder="Cheque number, transaction ID, etc."
                            />
                            <Input
                                label="Total Amount"
                                name="amount"
                                type="number"
                                step="0.01"
                                value={formData.amount}
                                onChange={handleChange}
                                error={errors.amount}
                                required
                            />
                        </div>
                    </div>

                    {formData.partner && invoices.length > 0 && (
                        <div className="form-section">
                            <h3 className="form-section-title">Invoice Allocation</h3>
                            <div className="invoice-allocation-table">
                                <div className="allocation-table-header">
                                    <div>Invoice #</div>
                                    <div>Date</div>
                                    <div>Total</div>
                                    <div>Outstanding</div>
                                    <div>Allocate Amount</div>
                                </div>
                                {invoices.map((invoice) => (
                                    <div key={invoice.id} className="allocation-table-row">
                                        <div>{invoice.invoice_number}</div>
                                        <div>{new Date(invoice.invoice_date).toLocaleDateString()}</div>
                                        <div>PKR {parseFloat(invoice.total_amount || 0).toLocaleString()}</div>
                                        <div>PKR {parseFloat(invoice.outstanding_amount || 0).toLocaleString()}</div>
                                        <div>
                                            <Input
                                                type="number"
                                                step="0.01"
                                                value={getAllocatedAmount(invoice.id)}
                                                onChange={(e) => handleInvoiceAllocation(invoice.id, parseFloat(e.target.value) || 0)}
                                                placeholder="0.00"
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

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
                            onClick={() => navigate('/accounting/payments')}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="primary"
                            loading={loading}
                        >
                            Record Payment
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default PaymentForm;
