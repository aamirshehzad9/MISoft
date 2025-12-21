import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import Select from '../../components/forms/Select'; // Import Select
import accountingService from '../../services/accounting';
import './InvoicesList.css'; // Reusing styles

const VoucherList = () => {
    const navigate = useNavigate();
    const [vouchers, setVouchers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterType, setFilterType] = useState('all'); // New Type Filter

    useEffect(() => {
        fetchVouchers();
    }, [filterStatus, filterType]);

    const fetchVouchers = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') {
                params.status = filterStatus;
            }
            if (filterType !== 'all') {
                params.voucher_type = filterType;
            }
            const data = await accountingService.getVouchers(params);
            setVouchers(data.results || data);
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

    const getTypeLabel = (type) => {
        const types = {
            JE: 'Journal Entry',
            CPV: 'Cash Payment',
            BPV: 'Bank Payment',
            CRV: 'Cash Receipt',
            BRV: 'Bank Receipt',
            DN: 'Debit Note',
            CN: 'Credit Note',
            CE: 'Contra Entry',
            SI: 'Sales Invoice',
            PI: 'Purchase Invoice'
        };
        return types[type] || type;
    };

    const columns = [
        {
            key: 'voucher_date',
            label: 'Date',
            sortable: true,
            width: '100px',
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
            width: '120px',
            render: (value) => (
                <Badge variant="info" size="sm">
                    {getTypeLabel(value)}
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
            render: (value) => value?.substring(0, 40) + (value?.length > 40 ? '...' : ''),
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

    const voucherTypes = [
        { value: 'all', label: 'All Types' },
        { value: 'JE', label: 'Journal Entry' },
        { value: 'CPV', label: 'Cash Payment' },
        { value: 'BPV', label: 'Bank Payment' },
        { value: 'CRV', label: 'Cash Receipt' },
        { value: 'BRV', label: 'Bank Receipt' },
        { value: 'DN', label: 'Debit Note' },
        { value: 'CN', label: 'Credit Note' },
        { value: 'CE', label: 'Contra Entry' },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card
                title="Vouchers"
                subtitle="Manage all financial transactions"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/accounting/vouchers/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        New Voucher
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input
                            placeholder="Search..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            icon={
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10zM14 14l-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            }
                        />
                    </div>

                    <div style={{ width: '200px' }}>
                        <Select
                            name="typeFilter"
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                            options={voucherTypes}
                            placeholder="Filter by Type"
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
                    emptyMessage="No vouchers found"
                    onRowClick={(row) => navigate(`/accounting/vouchers/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default VoucherList;
