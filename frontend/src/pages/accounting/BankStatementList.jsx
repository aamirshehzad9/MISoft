import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const BankStatementList = () => {
    const navigate = useNavigate();
    const [bankStatements, setBankStatements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchBankStatements();
    }, [filterStatus]);

    const fetchBankStatements = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'reconciled') params.is_reconciled = true;
            if (filterStatus === 'unreconciled') params.is_reconciled = false;
            const data = await accountingService.getBankStatements(params);
            setBankStatements(data.results || data);
        } catch (error) {
            console.error('Error fetching bank statements:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredBankStatements = bankStatements.filter(bs =>
        bs.bank_account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        bs.bank_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isReconciled) => {
        return isReconciled 
            ? { variant: 'success', label: 'Reconciled' }
            : { variant: 'warning', label: 'Unreconciled' };
    };

    const columns = [
        { 
            key: 'statement_date', 
            label: 'Date', 
            sortable: true, 
            width: '120px',
            render: (value) => new Date(value).toLocaleDateString()
        },
        { key: 'bank_name', label: 'Bank', sortable: true },
        { key: 'bank_account_name', label: 'Account', sortable: true },
        { 
            key: 'opening_balance', 
            label: 'Opening Balance', 
            sortable: true, 
            width: '150px',
            render: (value) => parseFloat(value).toFixed(2)
        },
        { 
            key: 'closing_balance', 
            label: 'Closing Balance', 
            sortable: true, 
            width: '150px',
            render: (value) => parseFloat(value).toFixed(2)
        },
        { 
            key: 'is_reconciled', 
            label: 'Status', 
            width: '120px',
            render: (value) => { 
                const badge = getStatusBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Bank Statements" 
                subtitle="Bank Statement Import and Management"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/bank-statements/new')}>
                        + New Bank Statement
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search bank statements..." 
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
                            variant={filterStatus === 'reconciled' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('reconciled')}
                        >
                            Reconciled
                        </Button>
                        <Button 
                            variant={filterStatus === 'unreconciled' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('unreconciled')}
                        >
                            Unreconciled
                        </Button>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredBankStatements} 
                    loading={loading} 
                    emptyMessage="No bank statements found" 
                    onRowClick={(bs) => navigate(`/dashboard/accounting/bank-statements/${bs.id}`)}
                />
            </Card>
        </div>
    );
};

export default BankStatementList;
