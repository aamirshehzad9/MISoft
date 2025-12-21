import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import {
    FaFolder, FaFolderOpen, FaFileInvoiceDollar, FaPlus, FaSearch,
    FaChevronRight, FaChevronDown, FaEdit, FaTrash
} from 'react-icons/fa';
import './ChartOfAccounts.css';

const AccountTreeItem = ({ account, children, level = 0, onToggle, isExpanded }) => {
    const hasChildren = children && children.length > 0;
    const paddingLeft = `${level * 24 + 12}px`;

    return (
        <div className="account-tree-item-container">
            <div
                className={`account-tree-row ${account.is_group ? 'is-group' : 'is-ledger'}`}
                style={{ paddingLeft }}
                onClick={() => hasChildren && onToggle(account.id)}
            >
                <div className="account-info-primary">
                    {hasChildren && (
                        <span className="toggle-icon">
                            {isExpanded ? <FaChevronDown /> : <FaChevronRight />}
                        </span>
                    )}
                    {!hasChildren && <span className="spacer-icon"></span>}

                    <span className="account-icon">
                        {account.is_group ? (
                            isExpanded ? <FaFolderOpen className="text-accent" /> : <FaFolder className="text-accent" />
                        ) : (
                            <FaFileInvoiceDollar className="text-muted" />
                        )}
                    </span>

                    <span className="account-code">{account.code}</span>
                    <span className="account-name">{account.name}</span>
                </div>

                <div className="account-info-secondary">
                    <span className={`account-type-badge type-${account.account_type}`}>
                        {account.account_type.replace('_', ' ')}
                    </span>
                    <span className="account-balance">
                        {parseFloat(account.current_balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                    <div className="account-actions">
                        <button className="btn-icon" title="Edit"><FaEdit /></button>
                    </div>
                </div>
            </div>

            {isExpanded && hasChildren && (
                <div className="account-children">
                    {children.map(child => (
                        <AccountTreeItem
                            key={child.id}
                            account={child}
                            children={child.children}
                            level={level + 1}
                            onToggle={onToggle}
                            isExpanded={child.isExpanded}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const ChartOfAccounts = () => {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedIds, setExpandedIds] = useState(new Set());

    useEffect(() => {
        fetchAccounts();
    }, []);

    const fetchAccounts = async () => {
        try {
            const response = await api.get('/accounting/accounts-v2/hierarchy/');
            const data = response.data;

            const flatAccounts = Array.isArray(data) ? data : (data.results || []);
            const tree = buildTree(flatAccounts);
            setAccounts(tree);

            // Auto-expand root nodes
            const rootIds = tree.map(node => node.id);
            setExpandedIds(new Set(rootIds));

            setLoading(false);
        } catch (error) {
            console.error('Error fetching accounts:', error);
            setError(error.message || 'Failed to load accounts');
            setLoading(false);
        }
    };

    const buildTree = (flatList) => {
        if (!flatList) return [];
        const map = {};
        const roots = [];

        // First pass: Initialize map
        flatList.forEach(node => {
            map[node.id] = { ...node, children: [], isExpanded: false };
        });

        // Second pass: Connect parents and children
        flatList.forEach(node => {
            if (node.parent) {
                if (map[node.parent]) {
                    map[node.parent].children.push(map[node.id]);
                }
            } else {
                roots.push(map[node.id]);
            }
        });

        return roots;
    };

    const toggleExpand = (id) => {
        setExpandedIds(prev => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    };

    // Recursive function to update expansion state for rendering
    const getRenderTree = (nodes) => {
        return nodes.map(node => ({
            ...node,
            isExpanded: expandedIds.has(node.id),
            children: getRenderTree(node.children)
        })).filter(node => {
            if (!searchTerm) return true;
            const matches = node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                node.code.includes(searchTerm);
            const hasMatchingChildren = node.children.length > 0;
            return matches || hasMatchingChildren;
        });
    };

    const renderTree = getRenderTree(accounts);

    return (
        <div className="coa-page">
            <div className="page-header">
                <div>
                    <h1>Chart of Accounts</h1>
                    <p className="text-muted">Manage your financial structure (V2 Enhanced)</p>
                </div>
                <button className="btn-primary">
                    <FaPlus /> New Account
                </button>
            </div>

            <div className="coa-toolbar">
                <div className="search-bar">
                    <FaSearch />
                    <input
                        type="text"
                        placeholder="Search by code or name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="toolbar-actions">
                    <button className="btn-secondary" onClick={() => setExpandedIds(new Set())}>Collapse All</button>
                </div>
            </div>

            <div className="coa-tree-container">
                <div className="tree-header">
                    <div className="col-name">Account Name</div>
                    <div className="col-type">Type</div>
                    <div className="col-balance">Balance</div>
                    <div className="col-actions">Actions</div>
                </div>

                {loading ? (
                    <div className="loading-state">Loading Chart of Accounts...</div>
                ) : error ? (
                    <div className="error-state" style={{ padding: '2rem', color: 'red' }}>
                        <h3>Error Loading Accounts</h3>
                        <p>{error}</p>
                    </div>
                ) : renderTree.length === 0 ? (
                    <div className="empty-state" style={{ padding: '2rem', textAlign: 'center' }}>
                        <p>No accounts found.</p>
                    </div>
                ) : (
                    <div className="tree-body">
                        {renderTree.map(root => (
                            <AccountTreeItem
                                key={root.id}
                                account={root}
                                children={root.children}
                                onToggle={toggleExpand}
                                isExpanded={root.isExpanded}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChartOfAccounts;
