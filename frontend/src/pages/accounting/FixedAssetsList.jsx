import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const FixedAssetsList = () => {
    const navigate = useNavigate();
    const [assets, setAssets] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterCategory, setFilterCategory] = useState('all');

    useEffect(() => {
        fetchAssets();
        fetchCategories();
    }, [filterStatus, filterCategory]);

    const fetchAssets = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;
            if (filterCategory !== 'all') params.asset_category = filterCategory;
            const data = await accountingService.getFixedAssets(params);
            setAssets(data.results || data);
        } catch (error) {
            console.error('Error fetching fixed assets:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const data = await accountingService.getAssetCategories();
            setCategories(data.results || data);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const filteredAssets = assets.filter(asset =>
        asset.asset_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.asset_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.asset_tag?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.location?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            active: { variant: 'success', label: 'Active' },
            disposed: { variant: 'danger', label: 'Disposed' },
            under_maintenance: { variant: 'warning', label: 'Under Maintenance' },
            retired: { variant: 'secondary', label: 'Retired' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-PK', {
            style: 'currency',
            currency: 'PKR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    const columns = [
        { key: 'asset_number', label: 'Asset #', sortable: true, width: '120px' },
        { key: 'asset_name', label: 'Asset Name', sortable: true },
        { key: 'category_name', label: 'Category', sortable: true },
        { key: 'acquisition_date', label: 'Acquisition Date', sortable: true, width: '130px', render: (value) => new Date(value).toLocaleDateString() },
        { key: 'book_value', label: 'Book Value', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'location', label: 'Location', sortable: true },
        { key: 'asset_tag', label: 'Tag', sortable: true, width: '100px' },
        { 
            key: 'status', 
            label: 'Status', 
            render: (value) => { 
                const badge = getStatusBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Fixed Assets" 
                subtitle="Manage fixed assets and equipment"
                action={
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <Button variant="secondary" size="sm" onClick={() => navigate('/accounting/fixed-assets/reports')}>
                            📊 Reports
                        </Button>
                        <Button variant="primary" size="sm" onClick={() => navigate('/accounting/fixed-assets/new')}>
                            + New Asset
                        </Button>
                    </div>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search assets..." 
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
                            variant={filterStatus === 'disposed' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('disposed')}
                        >
                            Disposed
                        </Button>
                        <Button 
                            variant={filterStatus === 'under_maintenance' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setFilterStatus('under_maintenance')}
                        >
                            Maintenance
                        </Button>
                    </div>
                    {categories.length > 0 && (
                        <div className="invoices-filter-buttons">
                            <select 
                                value={filterCategory} 
                                onChange={(e) => setFilterCategory(e.target.value)}
                                style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                            >
                                <option value="all">All Categories</option>
                                {categories.map(cat => (
                                    <option key={cat.id} value={cat.id}>{cat.category_name}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
                <Table 
                    columns={columns} 
                    data={filteredAssets} 
                    loading={loading} 
                    emptyMessage="No fixed assets found" 
                    onRowClick={(asset) => navigate(`/accounting/fixed-assets/${asset.id}`)}
                />
            </Card>
        </div>
    );
};

export default FixedAssetsList;
