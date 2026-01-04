import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const BankTransfers = () => {
    const navigate = useNavigate();
    const [transfers, setTransfers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchTransfers();
    }, [filterStatus]);

    const fetchTransfers = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;
            const data = await accountingService.getBankTransfers(params);
            setTransfers(data.results || data);
        } catch (error) {
            console.error('Error fetching transfers:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTransfers = transfers.filter(transfer =>
        transfer.transfer_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transfer.from_bank_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transfer.to_bank_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            pending: { variant: 'warning', label: 'Pending' },
            completed: { variant: 'success', label: 'Completed' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const getApprovalBadge = (status) => {
        const badges = {
            pending: { variant: 'warning', label: 'Pending' },
            approved: { variant: 'success', label: 'Approved' },
            rejected: { variant: 'danger', label: 'Rejected' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        { key: 'transfer_date', label: 'Date', sortable: true, width: '100px', render: (value) => new Date(value).toLocaleDateString() },
        { key: 'transfer_number', label: 'Transfer #', sortable: true, width: '120px' },
        { key: 'from_bank_name', label: 'From Bank', sortable: true },
        { key: 'to_bank_name', label: 'To Bank', sortable: true },
        { key: 'amount', label: 'Amount', sortable: true, render: (value) => PKR  },
        { key: 'status', label: 'Status', render: (value) => { const badge = getStatusBadge(value); return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; } },
        { key: 'approval_status', label: 'Approval', render: (value) => { const badge = getApprovalBadge(value); return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; } },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card title="Bank Transfers" subtitle="Manage inter-bank transfers">
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input placeholder="Search transfers..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button variant={filterStatus === 'all' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('all')}>All</Button>
                        <Button variant={filterStatus === 'pending' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('pending')}>Pending</Button>
                        <Button variant={filterStatus === 'completed' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterStatus('completed')}>Completed</Button>
                    </div>
                </div>
                <Table columns={columns} data={filteredTransfers} loading={loading} emptyMessage="No transfers found" />
            </Card>
        </div>
    );
};

export default BankTransfers;
