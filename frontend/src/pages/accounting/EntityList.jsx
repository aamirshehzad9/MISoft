import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const EntityList = () => {
    const navigate = useNavigate();
    const [entities, setEntities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchEntities();
    }, [filterStatus]);

    const fetchEntities = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus === 'active') params.is_active = true;
            if (filterStatus === 'inactive') params.is_active = false;
            const data = await accountingService.getEntities(params);
            setEntities(data.results || data);
        } catch (error) {
            console.error('Error fetching entities:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredEntities = entities.filter(ent =>
        ent.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ent.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ent.description?.toLowerCase().includes(searchTerm.toLowerCase())
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
                title="Entities (V2)" 
                subtitle="Multi-Entity Organizational Tracking"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/entities/new')}>
                        + New Entity
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search entities..." 
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
                    data={filteredEntities} 
                    loading={loading} 
                    emptyMessage="No entities found" 
                    onRowClick={(ent) => navigate(`/dashboard/accounting/entities/${ent.id}`)}
                />
            </Card>
        </div>
    );
};

export default EntityList;
