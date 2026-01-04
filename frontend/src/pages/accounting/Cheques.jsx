import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const Cheques = () => {
    const navigate = useNavigate();
    const [cheques, setCheques] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchCheques();
    }, [filterStatus]);

    const fetchCheques = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;
            const data = await accountingService.getCheques(params);
            setCheques(data.results || data);
        } catch (error) {
            console.error('Error fetching cheques:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredCheques = cheques.filter(cheque =>
        cheque.cheque_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cheque.payee_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            issued: { variant: 'info', label: 'Issued' },
            cleared: { variant: 'success', label: 'Cleared' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        { key: 'cheque_date', label: 'Date', sortable: true, width: '100px', render: (value) => new Date(value).toLocaleDateString() },
        { key: 'cheque_number', label: 'Cheque #', sortable: true, width: '120px' },
        { key: 'bank_account_name', label: 'Bank Account', sortable: true },
        { key: 'payee_name', label: 'Payee', sortable: true },
        { key: 'amount', label: 'Amount', sortable: true, render: (value) => PKR  },
        { key: 'status', label: 'Status', render: (value) => { const badge = getStatusBadge(value); return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; } },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card title="Cheques" subtitle="Manage cheque payments">
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input placeholder="Search cheques..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button variant={filterStatus === 'all' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('all')}>All</Button>
                        <Button variant={filterStatus === 'issued' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('issued')}>Issued</Button>
                        <Button variant={filterStatus === 'cleared' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('cleared')}>Cleared</Button>
                    </div>
                </div>
                <Table columns={columns} data={filteredCheques} loading={loading} emptyMessage="No cheques found" />
            </Card>
        </div>
    );
};

export default Cheques;
