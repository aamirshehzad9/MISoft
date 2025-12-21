import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const InvoicesList = () => {
    const navigate = useNavigate();
    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');

    useEffect(() => {
        fetchInvoices();
    }, [filterType]);

    const fetchInvoices = async () => {
        try {
            setLoading(true);
            let data;
            if (filterType === 'sales') {
                data = await accountingService.getSalesInvoices();
            } else if (filterType === 'purchase') {
                data = await accountingService.getPurchaseInvoices();
            } else if (filterType === 'overdue') {
                data = await accountingService.getOverdueInvoices();
            } else {
                data = await accountingService.getInvoices();
            }
            setInvoices(data);
        } catch (error) {
            console.error('Error fetching invoices:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredInvoices = invoices.filter(invoice =>
        invoice.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.partner_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            draft: { variant: 'default', label: 'Draft' },
            submitted: { variant: 'info', label: 'Submitted' },
            paid: { variant: 'success', label: 'Paid' },
            partially_paid: { variant: 'warning', label: 'Partially Paid' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        {
            key: 'invoice_number',
            label: 'Invoice #',
            sortable: true,
            width: '140px',
        },
        {
            key: 'invoice_type',
            label: 'Type',
            render: (value) => (
                <Badge variant={value === 'sales' ? 'success' : 'info'} size="sm">
                    {value === 'sales' ? 'Sales' : 'Purchase'}
                </Badge>
            ),
        },
        {
            key: 'partner_name',
            label: 'Partner',
            sortable: true,
        },
        {
            key: 'invoice_date',
            label: 'Date',
            sortable: true,
            render: (value) => new Date(value).toLocaleDateString(),
        },
        {
            key: 'total_amount',
            label: 'Total',
            sortable: true,
            render: (value) => `PKR ${parseFloat(value || 0).toLocaleString()}`,
        },
        {
            key: 'outstanding_amount',
            label: 'Outstanding',
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
        <div className="invoices-list-page">
            <Card
                title="Invoices"
                subtitle="Manage sales and purchase invoices"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/accounting/invoices/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        New Invoice
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input
                            placeholder="Search by invoice number or partner..."
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
                            variant={filterType === 'all' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('all')}
                        >
                            All
                        </Button>
                        <Button
                            variant={filterType === 'sales' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('sales')}
                        >
                            Sales
                        </Button>
                        <Button
                            variant={filterType === 'purchase' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('purchase')}
                        >
                            Purchase
                        </Button>
                        <Button
                            variant={filterType === 'overdue' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('overdue')}
                        >
                            Overdue
                        </Button>
                    </div>
                </div>

                <Table
                    columns={columns}
                    data={filteredInvoices}
                    loading={loading}
                    emptyMessage="No invoices found"
                    onRowClick={(row) => navigate(`/accounting/invoices/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default InvoicesList;
