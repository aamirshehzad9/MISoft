import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const BankReconciliation = () => {
    const navigate = useNavigate();
    const [reconciliations, setReconciliations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchReconciliations();
    }, [filterStatus]);

    const fetchReconciliations = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;
            const data = await accountingService.getBankReconciliations(params);
            setReconciliations(data.results || data);
        } catch (error) {
            console.error('Error fetching reconciliations:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredReconciliations = reconciliations.filter(rec =>
        rec.bank_account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rec.reconciliation_date?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            pending: { variant: 'warning', label: 'Pending' },
            completed: { variant: 'success', label: 'Completed' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        { key: 'reconciliation_date', label: 'Date', sortable: true, width: '120px', render: (value) => new Date(value).toLocaleDateString() },
        { key: 'bank_account_name', label: 'Bank Account', sortable: true },
        { key: 'statement_balance', label: 'Statement Balance', sortable: true, render: (value) => `PKR ${parseFloat(value).toLocaleString()}` },
        { key: 'ledger_balance', label: 'Ledger Balance', sortable: true, render: (value) => `PKR ${parseFloat(value).toLocaleString()}` },
        { key: 'difference', label: 'Difference', sortable: true, render: (value) => `PKR ${parseFloat(value).toLocaleString()}` },
        { key: 'status', label: 'Status', render: (value) => { const badge = getStatusBadge(value); return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; } },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card title="Bank Reconciliation" subtitle="Manage bank reconciliation statements">
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input placeholder="Search reconciliations..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button variant={filterStatus === 'all' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('all')}>All</Button>
                        <Button variant={filterStatus === 'pending' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('pending')}>Pending</Button>
                        <Button variant={filterStatus === 'completed' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('completed')}>Completed</Button>
                    </div>
                </div>
                <Table columns={columns} data={filteredReconciliations} loading={loading} emptyMessage="No reconciliations found" />
            </Card>
        </div>
    );
};

export default BankReconciliation;
