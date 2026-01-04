import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const FairValueList = () => {
    const navigate = useNavigate();
    const [fairValues, setFairValues] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterLevel, setFilterLevel] = useState('all');

    useEffect(() => {
        fetchFairValues();
    }, [filterLevel]);

    const fetchFairValues = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterLevel !== 'all') params.level = filterLevel;
            const data = await accountingService.getFairValueMeasurements(params);
            setFairValues(data.results || data);
        } catch (error) {
            console.error('Error fetching fair value measurements:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredFairValues = fairValues.filter(fv =>
        fv.asset_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        fv.asset_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        fv.valuation_technique?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getLevelBadge = (level) => {
        const badges = {
            '1': { variant: 'success', label: 'Level 1' },
            '2': { variant: 'warning', label: 'Level 2' },
            '3': { variant: 'danger', label: 'Level 3' }
        };
        return badges[level] || { variant: 'secondary', label: 'Unknown' };
    };

    const columns = [
        { 
            key: 'measurement_date', 
            label: 'Date', 
            sortable: true, 
            width: '120px',
            render: (value) => new Date(value).toLocaleDateString()
        },
        { key: 'asset_code', label: 'Asset Code', sortable: true, width: '120px' },
        { key: 'asset_name', label: 'Asset Name', sortable: true },
        { 
            key: 'fair_value', 
            label: 'Fair Value', 
            sortable: true, 
            width: '150px',
            render: (value) => parseFloat(value).toFixed(2)
        },
        { key: 'valuation_technique', label: 'Valuation Technique', sortable: true },
        { 
            key: 'level', 
            label: 'IFRS Level', 
            width: '120px',
            render: (value) => { 
                const badge = getLevelBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Fair Value Measurements" 
                subtitle="IAS 39 / IFRS 9 Compliance"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/fair-value-measurements/new')}>
                        + New Fair Value Measurement
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search fair value measurements..." 
                            value={searchTerm} 
                            onChange={(e) => setSearchTerm(e.target.value)} 
                        />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button 
                            variant={filterLevel === 'all' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterLevel('all')}
                        >
                            All Levels
                        </Button>
                        <Button 
                            variant={filterLevel === '1' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterLevel('1')}
                        >
                            Level 1
                        </Button>
                        <Button 
                            variant={filterLevel === '2' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterLevel('2')}
                        >
                            Level 2
                        </Button>
                        <Button 
                            variant={filterLevel === '3' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterLevel('3')}
                        >
                            Level 3
                        </Button>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredFairValues} 
                    loading={loading} 
                    emptyMessage="No fair value measurements found" 
                    onRowClick={(fv) => navigate(`/dashboard/accounting/fair-value-measurements/${fv.id}`)}
                />
            </Card>
        </div>
    );
};

export default FairValueList;
