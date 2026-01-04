import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
    const [expandedMenus, setExpandedMenus] = React.useState({
        accounting: true, // Default expanded for visibility
        banking: false,
        tax: false,
        masterData: false,
        assets: false,
        advanced: false
    });

    const toggleMenu = (key) => {
        setExpandedMenus(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    const menuItems = [
        {
            label: 'Dashboard',
            path: '/dashboard',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="currentColor" />
                </svg>
            ),
        },
        {
            label: 'Business Partners',
            path: '/dashboard/partners',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor" />
                </svg>
            ),
        },
        {
            label: 'Products',
            path: '/dashboard/products',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            ),
        },
        {
            label: 'Manufacturing',
            path: '/dashboard/manufacturing',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor" />
                </svg>
            ),
        },
        {
            label: 'Price Management',
            path: '/dashboard/pricing',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z" fill="currentColor" />
                </svg>
            ),
        },
        {
            label: 'UoM Converter',
            path: '/dashboard/uom-converter',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor" />
                </svg>
            ),
        },
        {
            label: 'Accounting',
            key: 'accounting',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" fill="currentColor" />
                </svg>
            ),
            children: [
                { label: 'Invoices', path: '/dashboard/accounting/invoices' },
                { label: 'Vouchers', path: '/dashboard/accounting/vouchers' },
                { label: 'Chart of Accounts', path: '/dashboard/accounting/chart-of-accounts' },
                { label: 'Payments', path: '/dashboard/accounting/payments' },
                { 
                    label: 'Banking', 
                    key: 'banking',
                    isSubGroup: true,
                    children: [
                        { label: 'Bank Accounts', path: '/dashboard/accounting/bank-accounts' },
                        { label: 'Bank Statements', path: '/dashboard/accounting/bank-statements' },
                        { label: 'Bank Transfers', path: '/dashboard/accounting/bank-transfers' },
                        { label: 'Bank Reconciliation', path: '/dashboard/accounting/bank-reconciliation' },
                        { label: 'Cheques', path: '/dashboard/accounting/cheques' },
                    ]
                },
                { 
                    label: 'Tax Management', 
                    key: 'tax',
                    isSubGroup: true,
                    children: [
                        { label: 'Tax Codes', path: '/dashboard/accounting/tax-codes' },
                        { label: 'Tax Masters', path: '/dashboard/accounting/tax-masters' },
                        { label: 'Tax Groups', path: '/dashboard/accounting/tax-groups' },
                    ]
                },
                { 
                    label: 'Master Data', 
                    key: 'masterData',
                    isSubGroup: true,
                    children: [
                        { label: 'Currencies', path: '/dashboard/accounting/currencies' },
                        { label: 'Exchange Rates', path: '/dashboard/accounting/exchange-rates' },
                        { label: 'Cost Centers', path: '/dashboard/accounting/cost-centers' },
                        { label: 'Departments', path: '/dashboard/accounting/departments' },
                        { label: 'Entities', path: '/dashboard/accounting/entities' },
                    ]
                },
                { 
                    label: 'Assets', 
                    key: 'assets',
                    isSubGroup: true,
                    children: [
                        { label: 'Fixed Assets', path: '/dashboard/accounting/fixed-assets' },
                        { label: 'Fair Value Measurements', path: '/dashboard/accounting/fair-value-measurements' },
                    ]
                },
                { 
                    label: 'Advanced', 
                    key: 'advanced',
                    isSubGroup: true,
                    children: [
                        { label: 'FX Revaluation Logs', path: '/dashboard/accounting/fx-revaluation-logs' },
                    ]
                },
                { label: 'Fiscal Years', path: '/dashboard/accounting/fiscal-years' },
                { label: 'Audit Trail', path: '/dashboard/accounting/audit-trail' },
                { label: 'Numbering Schemes', path: '/dashboard/accounting/numbering-schemes' },
            ]
        },
    ];

    const renderSubNav = (children, level = 0) => {
        return children.map(child => {
            if (child.isSubGroup) {
                // Render sub-group with nested items
                return (
                    <div key={child.key} style={{ marginLeft: level > 0 ? '0' : '0' }}>
                        <div
                            className="sidebar-subgroup-header"
                            onClick={() => toggleMenu(child.key)}
                        >
                            <span className="sidebar-subgroup-label">{child.label}</span>
                            <span className={`sidebar-nav-chevron ${expandedMenus[child.key] ? 'expanded' : ''}`}>
                                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                                    <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            </span>
                        </div>
                        {expandedMenus[child.key] && (
                            <div className="sidebar-subgroup-items">
                                {child.children.map(subChild => (
                                    <NavLink
                                        key={subChild.path}
                                        to={subChild.path}
                                        className={({ isActive }) =>
                                            `sidebar-subnav-item ${isActive ? 'active' : ''}`
                                        }
                                        onClick={onClose}
                                    >
                                        {subChild.label}
                                    </NavLink>
                                ))}
                            </div>
                        )}
                    </div>
                );
            } else {
                // Regular menu item
                return (
                    <NavLink
                        key={child.path}
                        to={child.path}
                        className={({ isActive }) =>
                            `sidebar-subnav-item ${isActive ? 'active' : ''}`
                        }
                        onClick={onClose}
                    >
                        {child.label}
                    </NavLink>
                );
            }
        });
    };

    return (
        <>
            {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}
            <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <img src="/logo.png" alt="MISoft" className="sidebar-logo-img" />
                        <span className="sidebar-logo-text">MISoft</span>
                    </div>
                </div>
                <nav className="sidebar-nav">
                    {menuItems.map((item) => (
                        <div key={item.label}>
                            {item.children ? (
                                <>
                                    <div
                                        className={`sidebar-nav-item ${expandedMenus[item.key] ? 'expanded' : ''}`}
                                        onClick={() => toggleMenu(item.key)}
                                    >
                                        <span className="sidebar-nav-icon">{item.icon}</span>
                                        <span className="sidebar-nav-label">{item.label}</span>
                                        <span className={`sidebar-nav-chevron ${expandedMenus[item.key] ? 'expanded' : ''}`}>
                                            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                                <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                        </span>
                                    </div>
                                    {expandedMenus[item.key] && (
                                        <div className="sidebar-subnav">
                                            {renderSubNav(item.children)}
                                        </div>
                                    )}
                                </>
                            ) : (
                                <NavLink
                                    to={item.path}
                                    className={({ isActive }) =>
                                        `sidebar-nav-item ${isActive ? 'active' : ''}`
                                    }
                                    onClick={onClose}
                                >
                                    <span className="sidebar-nav-icon">{item.icon}</span>
                                    <span className="sidebar-nav-label">{item.label}</span>
                                </NavLink>
                            )}
                        </div>
                    ))}
                </nav>
            </aside>
        </>
    );
};

export default Sidebar;

