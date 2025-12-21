import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import './Dashboard.css';

const Dashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalPartners: 0,
        totalProducts: 0,
        activeOrders: 0,
        pendingInvoices: 0,
        monthlyRevenue: 0,
        inventoryValue: 0,
    });

    useEffect(() => {
        // In a real app, fetch these stats from API
        // For now, using placeholder data
        setStats({
            totalPartners: 0,
            totalProducts: 0,
            activeOrders: 0,
            pendingInvoices: 0,
            monthlyRevenue: 0,
            inventoryValue: 0,
        });
    }, []);

    const kpiCards = [
        {
            title: 'Total Partners',
            value: stats.totalPartners,
            icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor" />
                </svg>
            ),
            color: 'primary',
            link: '/partners',
        },
        {
            title: 'Total Products',
            value: stats.totalProducts,
            icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            ),
            color: 'success',
            link: '/products',
        },
        {
            title: 'Active Orders',
            value: stats.activeOrders,
            icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor" />
                </svg>
            ),
            color: 'warning',
            link: '/manufacturing/production-orders',
        },
        {
            title: 'Pending Invoices',
            value: stats.pendingInvoices,
            icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z" fill="currentColor" />
                </svg>
            ),
            color: 'danger',
            link: '/accounting/invoices',
        },
    ];

    const quickActions = [
        {
            label: 'New Partner',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor" />
                </svg>
            ),
            onClick: () => navigate('/partners/new'),
            variant: 'primary',
        },
        {
            label: 'New Product',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor" />
                </svg>
            ),
            onClick: () => navigate('/products/new'),
            variant: 'success',
        },
        {
            label: 'New Production Order',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor" />
                </svg>
            ),
            onClick: () => navigate('/manufacturing/production-orders/new'),
            variant: 'warning',
        },
        {
            label: 'New Invoice',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor" />
                </svg>
            ),
            onClick: () => navigate('/accounting/invoices/new'),
            variant: 'info',
        },
    ];

    const recentActivities = [
        // Placeholder data - in real app, fetch from API
    ];

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <div>
                    <h1 className="dashboard-title">Welcome back, {user?.first_name || user?.username}!</h1>
                    <p className="dashboard-subtitle">Here's what's happening with your business today.</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="kpi-grid">
                {kpiCards.map((kpi, index) => (
                    <Card key={index} className="kpi-card" padding="md">
                        <div className="kpi-content">
                            <div className={`kpi-icon kpi-icon-${kpi.color}`}>
                                {kpi.icon}
                            </div>
                            <div className="kpi-details">
                                <h3 className="kpi-title">{kpi.title}</h3>
                                <p className="kpi-value">{kpi.value}</p>
                            </div>
                        </div>
                        <button className="kpi-link" onClick={() => navigate(kpi.link)}>
                            View Details →
                        </button>
                    </Card>
                ))}
            </div>

            {/* Quick Actions */}
            <Card title="Quick Actions" className="quick-actions-card">
                <div className="quick-actions-grid">
                    {quickActions.map((action, index) => (
                        <Button
                            key={index}
                            variant={action.variant}
                            onClick={action.onClick}
                            icon={action.icon}
                            className="quick-action-btn"
                        >
                            {action.label}
                        </Button>
                    ))}
                </div>
            </Card>

            {/* Charts Section */}
            <div className="charts-grid">
                <Card title="Monthly Revenue" subtitle="Last 6 months" className="chart-card">
                    <div className="chart-placeholder">
                        <div className="chart-bars">
                            {[65, 45, 80, 55, 70, 90].map((height, index) => (
                                <div key={index} className="chart-bar-container">
                                    <div className="chart-bar" style={{ height: `${height}%` }}></div>
                                    <span className="chart-label">M{index + 1}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </Card>

                <Card title="Production Status" subtitle="Current month" className="chart-card">
                    <div className="chart-placeholder">
                        <div className="donut-chart">
                            <div className="donut-segment donut-completed"></div>
                            <div className="donut-center">
                                <div className="donut-value">0%</div>
                                <div className="donut-label">Completed</div>
                            </div>
                        </div>
                        <div className="donut-legend">
                            <div className="legend-item">
                                <span className="legend-color legend-completed"></span>
                                <span>Completed: 0</span>
                            </div>
                            <div className="legend-item">
                                <span className="legend-color legend-progress"></span>
                                <span>In Progress: 0</span>
                            </div>
                            <div className="legend-item">
                                <span className="legend-color legend-planned"></span>
                                <span>Planned: 0</span>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Recent Activities */}
            <Card title="Recent Activities" subtitle="Latest updates across all modules">
                {recentActivities.length === 0 ? (
                    <div className="empty-activities">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor" opacity="0.3" />
                        </svg>
                        <p>No recent activities</p>
                        <p className="empty-subtitle">Start by creating partners, products, or orders</p>
                    </div>
                ) : (
                    <div className="activities-list">
                        {recentActivities.map((activity, index) => (
                            <div key={index} className="activity-item">
                                <div className="activity-icon">
                                    <Badge variant={activity.type}>{activity.type}</Badge>
                                </div>
                                <div className="activity-content">
                                    <p className="activity-text">{activity.text}</p>
                                    <span className="activity-time">{activity.time}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </Card>
        </div>
    );
};

export default Dashboard;
