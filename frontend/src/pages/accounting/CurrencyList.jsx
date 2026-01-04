import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const CurrencyList = () => {
    const navigate = useNavigate();
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchCurrencies();
    }, [filterStatus]);

    const fetchCurrencies = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            const data = await accountingService.getCurrencies(params);
            setCurrencies(data.results || data);
        } catch (error) {
            console.error('Error fetching currencies:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredCurrencies = currencies.filter(c =>
        c.currency_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.currency_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isActive) => {
        return isActive 
            ? { variant: 'success', label: 'Active' }
            : { variant: 'secondary', label: 'Inactive' };
    };

    const columns = [
        { key: 'currency_code', label: 'Code', sortable: true, width: '100px' },
        { key: 'currency_name', label: 'Currency Name', sortable: true },
        { key: 'symbol', label: 'Symbol', sortable: true, width: '100px' },
        { 
            key: 'is_base_currency', 
            label: 'Base', 
            width: '80px',
            render: (value) => value ? <Badge variant="primary" size="sm">Base</Badge> : '-'
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
                title="Currencies (V2)" 
                subtitle="IAS 21 Compliant Currency Management"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/currencies/new')}>
                        + New Currency
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search currencies..." 
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
                    data={filteredCurrencies} 
                    loading={loading} 
                    emptyMessage="No currencies found" 
                    onRowClick={(c) => navigate(`/dashboard/accounting/currencies/${c.id}`)}
                />
            </Card>
        </div>
    );
};

export default CurrencyList;
