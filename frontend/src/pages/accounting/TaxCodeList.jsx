import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const TaxCodeList = () => {
    const navigate = useNavigate();
    const [taxCodes, setTaxCodes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchTaxCodes();
    }, [filterStatus]);

    const fetchTaxCodes = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            const data = await accountingService.getTaxCodes(params);
            setTaxCodes(data.results || data);
        } catch (error) {
            console.error('Error fetching tax codes:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTaxCodes = taxCodes.filter(tc =>
        tc.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tc.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isActive) => {
        return isActive 
            ? { variant: 'success', label: 'Active' }
            : { variant: 'secondary', label: 'Inactive' };
    };

    const columns = [
        { key: 'code', label: 'Tax Code', sortable: true, width: '120px' },
        { key: 'description', label: 'Description', sortable: true },
        { 
            key: 'tax_percentage', 
            label: 'Tax Rate', 
            sortable: true, 
            width: '100px',
            render: (value) => `${value}%`
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
                title="Tax Codes" 
                subtitle="Manage tax rates and codes"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/tax-codes/new')}>
                        + New Tax Code
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search tax codes..." 
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
                    data={filteredTaxCodes} 
                    loading={loading} 
                    emptyMessage="No tax codes found" 
                    onRowClick={(tc) => navigate(`/dashboard/accounting/tax-codes/${tc.id}`)}
                />
            </Card>
        </div>
    );
};

export default TaxCodeList;
