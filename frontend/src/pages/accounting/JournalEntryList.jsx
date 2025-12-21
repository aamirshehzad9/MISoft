import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css'; // Reusing styles for now

const JournalEntryList = () => {
    const navigate = useNavigate();
    const [vouchers, setVouchers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchVouchers();
    }, [filterStatus]);

    const fetchVouchers = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') {
                params.status = filterStatus;
            }
            const data = await accountingService.getVouchers(params);
            setVouchers(data.results || data); // Handle pagination if present
        } catch (error) {
            console.error('Error fetching vouchers:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredVouchers = vouchers.filter(voucher =>
        voucher.voucher_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        voucher.reference_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        voucher.narration?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            draft: { variant: 'default', label: 'Draft' },
            posted: { variant: 'success', label: 'Posted' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        {
            key: 'voucher_date',
            label: 'Date',
            sortable: true,
            width: '120px',
            render: (value) => new Date(value).toLocaleDateString(),
        },
        {
            key: 'voucher_number',
            label: 'Voucher #',
            sortable: true,
            width: '140px',
        },
        {
            key: 'voucher_type',
            label: 'Type',
            width: '100px',
            render: (value) => (
                <Badge variant="info" size="sm">
                    {value}
                </Badge>
            ),
        },
        {
            key: 'reference_number',
            label: 'Reference',
            sortable: true,
        },
        {
            key: 'narration',
            label: 'Narration',
            sortable: true,
            render: (value) => value?.substring(0, 50) + (value?.length > 50 ? '...' : ''),
        },
        {
            key: 'total_amount',
            label: 'Amount',
            sortable: true,
            render: (value) => `PKR ${parseFloat(value || 0).toLocaleString()}`,
        },
        {
            key: 'status',
            label: 'Status',
            render: (value) => {
                const badge = getStatusBadge(value);
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>;
            },
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card
                title="Journal Entries"
                subtitle="Manage financial transactions (Double-Entry)"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/accounting/journal-entries/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        New Entry
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input
                            placeholder="Search by number, reference or narration..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            icon={
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10zM14 14l-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            }
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
                            variant={filterStatus === 'draft' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterStatus('draft')}
                        >
                            Draft
                        </Button>
                        <Button
                            variant={filterStatus === 'posted' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterStatus('posted')}
                        >
                            Posted
                        </Button>
                    </div>
                </div>

                <Table
                    columns={columns}
                    data={filteredVouchers}
                    loading={loading}
                    emptyMessage="No journal entries found"
                    onRowClick={(row) => navigate(`/accounting/journal-entries/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default JournalEntryList;
