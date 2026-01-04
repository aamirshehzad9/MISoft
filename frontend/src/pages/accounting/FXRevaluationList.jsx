import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const FXRevaluationList = () => {
    const navigate = useNavigate();
    const [fxRevaluations, setFXRevaluations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchFXRevaluations();
    }, [filterStatus]);

    const fetchFXRevaluations = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;
            const data = await accountingService.getFXRevaluationLogs(params);
            setFXRevaluations(data.results || data);
        } catch (error) {
            console.error('Error fetching FX revaluation logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredFXRevaluations = fxRevaluations.filter(fx =>
        fx.revaluation_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        fx.entity_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        fx.entity_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            'initiated': { variant: 'secondary', label: 'Initiated' },
            'calculated': { variant: 'warning', label: 'Calculated' },
            'posted': { variant: 'success', label: 'Posted' },
            'reversed': { variant: 'danger', label: 'Reversed' },
            'error': { variant: 'danger', label: 'Error' }
        };
        return badges[status] || { variant: 'secondary', label: status };
    };

    const columns = [
        { key: 'revaluation_id', label: 'Revaluation ID', sortable: true, width: '150px' },
        { 
            key: 'revaluation_date', 
            label: 'Date', 
            sortable: true, 
            width: '120px',
            render: (value) => new Date(value).toLocaleDateString()
        },
        { key: 'entity_code', label: 'Entity', sortable: true, width: '100px' },
        { key: 'currency_code', label: 'Currency', sortable: true, width: '100px' },
        { 
            key: 'accounts_revalued', 
            label: 'Accounts', 
            sortable: true, 
            width: '100px'
        },
        { 
            key: 'net_fx_gain_loss', 
            label: 'Net FX Gain/(Loss)', 
            sortable: true, 
            width: '150px',
            render: (value) => {
                const num = parseFloat(value);
                const color = num >= 0 ? 'green' : 'red';
                return <span style={{ color }}>{num.toFixed(2)}</span>;
            }
        },
        { 
            key: 'status', 
            label: 'Status', 
            width: '120px',
            render: (value) => { 
                const badge = getStatusBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="FX Revaluation Logs" 
                subtitle="IAS 21 - Foreign Exchange Revaluation"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/fx-revaluation-logs/new')}>
                        + New FX Revaluation
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search FX revaluations..." 
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
                            variant={filterStatus === 'posted' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('posted')}
                        >
                            Posted
                        </Button>
                        <Button 
                            variant={filterStatus === 'calculated' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('calculated')}
                        >
                            Calculated
                        </Button>
                        <Button 
                            variant={filterStatus === 'error' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('error')}
                        >
                            Error
                        </Button>
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredFXRevaluations} 
                    loading={loading} 
                    emptyMessage="No FX revaluation logs found" 
                    onRowClick={(fx) => navigate(`/dashboard/accounting/fx-revaluation-logs/${fx.id}`)}
                />
            </Card>
        </div>
    );
};

export default FXRevaluationList;
