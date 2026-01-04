import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const FixedAssetsReports = () => {
    const navigate = useNavigate();
    const [activeReport, setActiveReport] = useState('register');
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchReport();
    }, [activeReport]);

    const fetchReport = async () => {
        try {
            setLoading(true);
            let data;
            switch (activeReport) {
                case 'register':
                    data = await accountingService.getFixedAssetRegister();
                    break;
                case 'category':
                    data = await accountingService.getAssetsByCategoryReport();
                    break;
                case 'location':
                    data = await accountingService.getAssetsByLocationReport();
                    break;
                default:
                    data = null;
            }
            setReportData(data);
        } catch (error) {
            console.error('Error fetching report:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-PK', {
            style: 'currency',
            currency: 'PKR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    const getStatusBadge = (status) => {
        const badges = {
            active: { variant: 'success', label: 'Active' },
            disposed: { variant: 'danger', label: 'Disposed' },
            under_maintenance: { variant: 'warning', label: 'Under Maintenance' },
            retired: { variant: 'secondary', label: 'Retired' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    // Fixed Asset Register Columns
    const registerColumns = [
        { key: 'asset_number', label: 'Asset #', sortable: true, width: '120px' },
        { key: 'asset_name', label: 'Asset Name', sortable: true },
        { key: 'category_name', label: 'Category', sortable: true },
        { key: 'acquisition_date', label: 'Acq. Date', sortable: true, width: '110px', render: (value) => new Date(value).toLocaleDateString() },
        { key: 'acquisition_cost', label: 'Cost', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'accumulated_depreciation', label: 'Depreciation', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'book_value', label: 'Book Value', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'location', label: 'Location', sortable: true },
        { 
            key: 'status', 
            label: 'Status', 
            render: (value) => { 
                const badge = getStatusBadge(value); 
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>; 
            } 
        },
    ];

    // Category Report Columns
    const categoryColumns = [
        { key: 'category_code', label: 'Code', sortable: true, width: '100px' },
        { key: 'category_name', label: 'Category', sortable: true },
        { key: 'asset_count', label: 'Assets', sortable: true, width: '80px' },
        { key: 'total_acquisition_cost', label: 'Total Cost', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'total_accumulated_depreciation', label: 'Total Depreciation', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'total_book_value', label: 'Total Book Value', sortable: true, render: (value) => formatCurrency(value) },
    ];

    // Location Report Columns
    const locationColumns = [
        { key: 'location', label: 'Location', sortable: true },
        { key: 'asset_count', label: 'Assets', sortable: true, width: '80px' },
        { key: 'total_acquisition_cost', label: 'Total Cost', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'total_accumulated_depreciation', label: 'Total Depreciation', sortable: true, render: (value) => formatCurrency(value) },
        { key: 'total_book_value', label: 'Total Book Value', sortable: true, render: (value) => formatCurrency(value) },
    ];

    const renderSummary = () => {
        if (!reportData || !reportData.summary) return null;

        const { summary } = reportData;

        return (
            <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                gap: '15px', 
                marginBottom: '20px',
                padding: '15px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px'
            }}>
                {summary.total_assets !== undefined && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Assets</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>{summary.total_assets}</div>
                    </div>
                )}
                {summary.total_categories !== undefined && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Categories</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>{summary.total_categories}</div>
                    </div>
                )}
                {summary.total_locations !== undefined && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Locations</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>{summary.total_locations}</div>
                    </div>
                )}
                {summary.total_acquisition_cost && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Acquisition Cost</div>
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#0066cc' }}>{formatCurrency(summary.total_acquisition_cost)}</div>
                    </div>
                )}
                {summary.total_accumulated_depreciation && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Depreciation</div>
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#dc3545' }}>{formatCurrency(summary.total_accumulated_depreciation)}</div>
                    </div>
                )}
                {summary.total_book_value && (
                    <div>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Total Book Value</div>
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#28a745' }}>{formatCurrency(summary.total_book_value)}</div>
                    </div>
                )}
            </div>
        );
    };

    const getReportData = () => {
        if (!reportData) return [];
        switch (activeReport) {
            case 'register':
                return reportData.assets || [];
            case 'category':
                return reportData.categories || [];
            case 'location':
                return reportData.locations || [];
            default:
                return [];
        }
    };

    const getColumns = () => {
        switch (activeReport) {
            case 'register':
                return registerColumns;
            case 'category':
                return categoryColumns;
            case 'location':
                return locationColumns;
            default:
                return [];
        }
    };

    const getReportTitle = () => {
        switch (activeReport) {
            case 'register':
                return 'Fixed Asset Register (FAR)';
            case 'category':
                return 'Assets by Category';
            case 'location':
                return 'Assets by Location';
            default:
                return 'Asset Reports';
        }
    };

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Asset Reports" 
                subtitle="IAS 16 Compliant Reports"
                action={
                    <Button variant="secondary" size="sm" onClick={() => navigate('/accounting/fixed-assets')}>
                        ← Back to Assets
                    </Button>
                }
            >
                <div className="invoices-filters" style={{ marginBottom: '20px' }}>
                    <div className="invoices-filter-buttons">
                        <Button 
                            variant={activeReport === 'register' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setActiveReport('register')}
                        >
                            📊 Asset Register
                        </Button>
                        <Button 
                            variant={activeReport === 'category' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setActiveReport('category')}
                        >
                            📁 By Category
                        </Button>
                        <Button 
                            variant={activeReport === 'location' ? 'primary' : 'ghost'} 
                            size="sm" 
                            onClick={() => setActiveReport('location')}
                        >
                            📍 By Location
                        </Button>
                    </div>
                </div>

                <h3 style={{ marginBottom: '15px', color: '#333' }}>{getReportTitle()}</h3>
                
                {renderSummary()}

                <Table 
                    columns={getColumns()} 
                    data={getReportData()} 
                    loading={loading} 
                    emptyMessage="No data available" 
                />
            </Card>
        </div>
    );
};

export default FixedAssetsReports;
