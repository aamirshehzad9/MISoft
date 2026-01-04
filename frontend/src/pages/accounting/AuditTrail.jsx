import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const AuditTrail = () => {
    const navigate = useNavigate();
    const [auditLogs, setAuditLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterAction, setFilterAction] = useState('all');

    useEffect(() => {
        fetchAuditLogs();
    }, [filterAction]);

    const fetchAuditLogs = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterAction !== 'all') params.action = filterAction;
            const data = await accountingService.getAuditLogs(params);
            setAuditLogs(data.results || data);
        } catch (error) {
            console.error('Error fetching audit logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredLogs = auditLogs.filter(log =>
        log.model_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.changes?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getActionBadge = (action) => {
        const badges = {
            CREATE: { variant: 'success', label: 'Created' },
            UPDATE: { variant: 'info', label: 'Updated' },
            DELETE: { variant: 'danger', label: 'Deleted' },
        };
        return badges[action] || { variant: 'default', label: action };
    };

    const columns = [
        { key: 'timestamp', label: 'Timestamp', sortable: true, width: '180px', render: (value) => new Date(value).toLocaleString() },
        { key: 'user_name', label: 'User', sortable: true, width: '150px' },
        { key: 'model_name', label: 'Model', sortable: true, width: '150px' },
        { key: 'action', label: 'Action', width: '100px', render: (value) => { const badge = getActionBadge(value); return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; } },
        { key: 'object_id', label: 'Object ID', width: '100px' },
        { key: 'changes', label: 'Changes', render: (value) => <span className="text-truncate" title={value}>{value?.substring(0, 50)}...</span> },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card title="Audit Trail" subtitle="View system audit logs and changes">
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input placeholder="Search audit logs..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    </div>
                    <div className="invoices-filter-buttons">
                        <Button variant={filterAction === 'all' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterAction('all')}>All</Button>
                        <Button variant={filterAction === 'CREATE' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterAction('CREATE')}>Created</Button>
                        <Button variant={filterAction === 'UPDATE' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterAction('UPDATE')}>Updated</Button>
                        <Button variant={filterAction === 'DELETE' ? 'primary' : 'ghost'} size="sm" onClick={() => setFilterAction('DELETE')}>Deleted</Button>
                    </div>
                </div>
                <Table columns={columns} data={filteredLogs} loading={loading} emptyMessage="No audit logs found" />
            </Card>
        </div>
    );
};

export default AuditTrail;
