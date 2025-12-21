import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import manufacturingService from '../../services/manufacturing';
import './ProductionOrdersList.css';

const ProductionOrdersList = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const data = await manufacturingService.getProductionOrders();
            setOrders(data);
        } catch (error) {
            console.error('Error fetching production orders:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredOrders = orders.filter(order =>
        order.order_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.product_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadge = (status) => {
        const badges = {
            draft: { variant: 'default', label: 'Draft' },
            planned: { variant: 'info', label: 'Planned' },
            released: { variant: 'primary', label: 'Released' },
            in_progress: { variant: 'warning', label: 'In Progress' },
            completed: { variant: 'success', label: 'Completed' },
            cancelled: { variant: 'danger', label: 'Cancelled' },
        };
        return badges[status] || { variant: 'default', label: status };
    };

    const columns = [
        {
            key: 'order_number',
            label: 'Order #',
            sortable: true,
            width: '140px',
        },
        {
            key: 'product_name',
            label: 'Product',
            sortable: true,
        },
        {
            key: 'planned_quantity',
            label: 'Planned Qty',
            sortable: true,
            render: (value, row) => `${value} ${row.uom_symbol || ''}`,
        },
        {
            key: 'produced_quantity',
            label: 'Produced',
            render: (value, row) => `${value} ${row.uom_symbol || ''}`,
        },
        {
            key: 'completion_percentage',
            label: 'Progress',
            render: (value) => (
                <div className="progress-cell">
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${value}%` }}></div>
                    </div>
                    <span className="progress-text">{Math.round(value)}%</span>
                </div>
            ),
        },
        {
            key: 'status',
            label: 'Status',
            render: (value) => {
                const badge = getStatusBadge(value);
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>;
            },
        },
        {
            key: 'planned_start_date',
            label: 'Start Date',
            render: (value) => new Date(value).toLocaleDateString(),
        },
    ];

    return (
        <div className="production-orders-page">
            <Card
                title="Production Orders"
                subtitle="Manage manufacturing work orders"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/manufacturing/production-orders/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        New Order
                    </Button>
                }
            >
                <div className="orders-filters">
                    <div className="orders-search">
                        <Input
                            placeholder="Search by order number or product..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            icon={
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10zM14 14l-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            }
                        />
                    </div>
                </div>

                <Table
                    columns={columns}
                    data={filteredOrders}
                    loading={loading}
                    emptyMessage="No production orders found"
                    onRowClick={(row) => navigate(`/manufacturing/production-orders/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default ProductionOrdersList;
