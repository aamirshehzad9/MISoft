import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import partnersService from '../../services/partners';
import './PartnersList.css';

const PartnersList = () => {
    const navigate = useNavigate();
    const [partners, setPartners] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all'); // all, customers, vendors

    useEffect(() => {
        fetchPartners();
    }, [filterType]);

    const fetchPartners = async () => {
        try {
            setLoading(true);
            let data;
            if (filterType === 'customers') {
                data = await partnersService.getCustomers();
            } else if (filterType === 'vendors') {
                data = await partnersService.getVendors();
            } else {
                data = await partnersService.getAll();
            }
            // Ensure data is an array
            setPartners(Array.isArray(data) ? data : (data?.results || []));
        } catch (error) {
            console.error('Error fetching partners:', error);
            setPartners([]); // Set empty array on error
        } finally {
            setLoading(false);
        }
    };

    const filteredPartners = partners.filter(partner =>
        partner.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        partner.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        partner.phone?.includes(searchTerm)
    );

    const columns = [
        {
            key: 'name',
            label: 'Name',
            sortable: true,
            render: (value, row) => (
                <div className="partner-name-cell">
                    <strong>{value}</strong>
                    {row.company_name && <div className="partner-company">{row.company_name}</div>}
                </div>
            ),
        },
        {
            key: 'type',
            label: 'Type',
            render: (_, row) => (
                <div className="partner-type-badges">
                    {row.is_customer && <Badge variant="primary" size="sm">Customer</Badge>}
                    {row.is_vendor && <Badge variant="info" size="sm">Vendor</Badge>}
                </div>
            ),
        },
        {
            key: 'email',
            label: 'Email',
            sortable: true,
        },
        {
            key: 'phone',
            label: 'Phone',
        },
        {
            key: 'outstanding_balance',
            label: 'Balance',
            sortable: true,
            render: (value) => `PKR ${parseFloat(value || 0).toLocaleString()}`,
        },
        {
            key: 'is_active',
            label: 'Status',
            render: (value) => (
                <Badge variant={value ? 'success' : 'danger'} size="sm">
                    {value ? 'Active' : 'Inactive'}
                </Badge>
            ),
        },
    ];

    return (
        <div className="partners-list-page">
            <Card
                title="Business Partners"
                subtitle="Manage customers and vendors"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/dashboard/partners/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        Add Partner
                    </Button>
                }
            >
                <div className="partners-filters">
                    <div className="partners-search">
                        <Input
                            placeholder="Search by name, email, or phone..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            icon={
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10zM14 14l-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            }
                        />
                    </div>
                    <div className="partners-filter-buttons">
                        <Button
                            variant={filterType === 'all' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('all')}
                        >
                            All
                        </Button>
                        <Button
                            variant={filterType === 'customers' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('customers')}
                        >
                            Customers
                        </Button>
                        <Button
                            variant={filterType === 'vendors' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('vendors')}
                        >
                            Vendors
                        </Button>
                    </div>
                </div>

                <Table
                    columns={columns}
                    data={filteredPartners}
                    loading={loading}
                    emptyMessage="No partners found"
                    onRowClick={(row) => navigate(`/partners/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default PartnersList;
