import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const TaxMasterList = () => {
    const navigate = useNavigate();
    const [taxMasters, setTaxMasters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterType, setFilterType] = useState('all');

    useEffect(() => {
        fetchTaxMasters();
    }, [filterStatus, filterType]);

    const fetchTaxMasters = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            if (filterType !== 'all') params.tax_type = filterType;
            const data = await accountingService.getTaxMasters(params);
            setTaxMasters(data.results || data);
        } catch (error) {
            console.error('Error fetching tax masters:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTaxMasters = taxMasters.filter(tm =>
        tm.tax_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tm.tax_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isActive) => {
        return isActive 
            ? { variant: 'success', label: 'Active' }
            : { variant: 'secondary', label: 'Inactive' };
    };

    const columns = [
        { key: 'tax_code', label: 'Tax Code', sortable: true, width: '120px' },
        { key: 'tax_name', label: 'Tax Name', sortable: true },
        { key: 'tax_type_display', label: 'Type', sortable: true, width: '120px' },
        { 
            key: 'tax_rate', 
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
                title="Tax Masters (V2)" 
                subtitle="IAS 12 Compliant Tax Management"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/tax-masters/new')}>
                        + New Tax Master
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search tax masters..." 
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
                    <div className="invoices-filter-buttons">
                        <select 
                            value={filterType} 
                            onChange={(e) => setFilterType(e.target.value)}
                            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                        >
                            <option value="all">All Types</option>
                            <option value="vat">VAT</option>
                            <option value="gst">GST</option>
                            <option value="sales_tax">Sales Tax</option>
                            <option value="service_tax">Service Tax</option>
                            <option value="excise">Excise Duty</option>
                            <option value="customs">Customs Duty</option>
                        </select>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredTaxMasters} 
                    loading={loading} 
                    emptyMessage="No tax masters found" 
                    onRowClick={(tm) => navigate(`/dashboard/accounting/tax-masters/${tm.id}`)}
                />
            </Card>
        </div>
    );
};

export default TaxMasterList;
