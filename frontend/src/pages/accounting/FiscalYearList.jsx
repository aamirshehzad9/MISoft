import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const FiscalYearList = () => {
    const navigate = useNavigate();
    const [fiscalYears, setFiscalYears] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchFiscalYears();
    }, [filterStatus]);

    const fetchFiscalYears = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'open') params.is_closed = false;
            if (filterStatus === 'closed') params.is_closed = true;
            const data = await accountingService.getFiscalYears(params);
            setFiscalYears(data.results || data);
        } catch (error) {
            console.error('Error fetching fiscal years:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredFiscalYears = fiscalYears.filter(fy =>
        fy.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isClosed) => {
        return isClosed 
            ? { variant: 'danger', label: 'Closed' }
            : { variant: 'success', label: 'Open' };
    };

    const columns = [
        { key: 'name', label: 'Fiscal Year', sortable: true },
        { 
            key: 'start_date', 
            label: 'Start Date', 
            sortable: true, 
            width: '130px',
            render: (value) => new Date(value).toLocaleDateString() 
        },
        { 
            key: 'end_date', 
            label: 'End Date', 
            sortable: true, 
            width: '130px',
            render: (value) => new Date(value).toLocaleDateString() 
        },
        { 
            key: 'is_closed', 
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
                title="Fiscal Years" 
                subtitle="Manage accounting periods"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/fiscal-years/new')}>
                        + New Fiscal Year
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search fiscal years..." 
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
                            variant={filterStatus === 'open' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('open')}
                        >
                            Open
                        </Button>
                        <Button 
                            variant={filterStatus === 'closed' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('closed')}
                        >
                            Closed
                        </Button>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredFiscalYears} 
                    loading={loading} 
                    emptyMessage="No fiscal years found" 
                    onRowClick={(fy) => navigate(`/dashboard/accounting/fiscal-years/${fy.id}`)}
                />
            </Card>
        </div>
    );
};

export default FiscalYearList;
