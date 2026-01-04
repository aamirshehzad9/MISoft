import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const BankAccountList = () => {
    const navigate = useNavigate();
    const [bankAccounts, setBankAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchBankAccounts();
    }, [filterStatus]);

    const fetchBankAccounts = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            const data = await accountingService.getBankAccounts(params);
            setBankAccounts(data.results || data);
        } catch (error) {
            console.error('Error fetching bank accounts:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredBankAccounts = bankAccounts.filter(ba =>
        ba.account_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ba.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ba.bank_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ba.branch?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isActive) => {
        return isActive 
            ? { variant: 'success', label: 'Active' }
            : { variant: 'secondary', label: 'Inactive' };
    };

    const columns = [
        { key: 'account_number', label: 'Account Number', sortable: true, width: '150px' },
        { key: 'account_name', label: 'Account Name', sortable: true },
        { key: 'bank_name', label: 'Bank Name', sortable: true },
        { key: 'branch', label: 'Branch', sortable: true },
        { 
            key: 'currency_code', 
            label: 'Currency', 
            sortable: true, 
            width: '100px'
        },
        { 
            key: 'current_balance', 
            label: 'Balance', 
            sortable: true, 
            width: '150px',
            render: (value, row) => `${row.currency_code} ${parseFloat(value).toFixed(2)}`
        },
        { 
            key: 'is_active', 
            label: 'Status', 
            width: '100px',
            render: (value) => { 
                const badge = getStatusBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Bank Accounts" 
                subtitle="Banking Operations Management"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/bank-accounts/new')}>
                        + New Bank Account
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search bank accounts..." 
                            value={searchTerm} 
                            onChange={(e) => setSearchTerm(e.target.value)} 
                        />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button 
                            variant={filterStatus === 'all' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('all')}
                        >
                            All
                        </Button>
                        <Button 
                            variant={filterStatus === 'active' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('active')}
                        >
                            Active
                        </Button>
                        <Button 
                            variant={filterStatus === 'inactive' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('inactive')}
                        >
                            Inactive
                        </Button>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredBankAccounts} 
                    loading={loading} 
                    emptyMessage="No bank accounts found" 
                    onRowClick={(ba) => navigate(`/dashboard/accounting/bank-accounts/${ba.id}`)}
                />
            </Card>
        </div>
    );
};

export default BankAccountList;
