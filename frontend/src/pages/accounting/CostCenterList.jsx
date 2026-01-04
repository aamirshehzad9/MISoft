import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const CostCenterList = () => {
    const navigate = useNavigate();
    const [costCenters, setCostCenters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchCostCenters();
    }, [filterStatus]);

    const fetchCostCenters = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            const data = await accountingService.getCostCenters(params);
            setCostCenters(data.results || data);
        } catch (error) {
            console.error('Error fetching cost centers:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredCostCenters = costCenters.filter(cc =>
        cc.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cc.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cc.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (isActive) => {
        return isActive 
            ? { variant: 'success', label: 'Active' }
            : { variant: 'secondary', label: 'Inactive' };
    };

    const columns = [
        { key: 'code', label: 'Code', sortable: true, width: '150px' },
        { key: 'name', label: 'Name', sortable: true },
        { key: 'description', label: 'Description', sortable: true },
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
                title="Cost Centers (V2)" 
                subtitle="Organizational Cost Tracking"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/cost-centers/new')}>
                        + New Cost Center
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search cost centers..." 
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
                    data={filteredCostCenters} 
                    loading={loading} 
                    emptyMessage="No cost centers found" 
                    onRowClick={(cc) => navigate(`/dashboard/accounting/cost-centers/${cc.id}`)}
                />
            </Card>
        </div>
    );
};

export default CostCenterList;
