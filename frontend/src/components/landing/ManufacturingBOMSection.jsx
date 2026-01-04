import React, { useState } from 'react';
import { Factory, Package, GitBranch, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react';
import './ManufacturingBOMSection.css';

const ManufacturingBOMSection = () => {
    const [activeTab, setActiveTab] = useState('bom');

    const bomLevels = [
        {
            level: 0,
            name: 'Finished Product',
            item: 'Premium Laptop Computer',
            quantity: 1,
            cost: '$1,200',
            children: true
        },
        {
            level: 1,
            name: 'Sub-Assembly',
            items: [
                { name: 'Motherboard Assembly', qty: 1, cost: '$350' },
                { name: 'Display Panel', qty: 1, cost: '$280' },
                { name: 'Battery Pack', qty: 1, cost: '$120' }
            ]
        },
        {
            level: 2,
            name: 'Raw Materials',
            items: [
                { name: 'CPU Processor', qty: 1, cost: '$180' },
                { name: 'RAM Modules', qty: 2, cost: '$80' },
                { name: 'LCD Screen', qty: 1, cost: '$200' },
                { name: 'Lithium Cells', qty: 6, cost: '$60' }
            ]
        }
    ];

    const workflowSteps = [
        {
            icon: <Package size={32} />,
            title: 'Material Planning',
            description: 'AI calculates material requirements based on production orders',
            status: 'active'
        },
        {
            icon: <Factory size={32} />,
            title: 'Production Execution',
            description: 'Track work orders and manufacturing progress in real-time',
            status: 'active'
        },
        {
            icon: <TrendingUp size={32} />,
            title: 'Cost Accounting',
            description: 'Automatic cost allocation and variance analysis',
            status: 'active'
        },
        {
            icon: <CheckCircle size={32} />,
            title: 'Financial Posting',
            description: 'Seamless integration with general ledger and inventory',
            status: 'active'
        }
    ];

    const features = [
        'Multi-level Bill of Materials (BOM)',
        'Work Order Management',
        'Production Planning & Scheduling',
        'Material Requirements Planning (MRP)',
        'Cost Accounting & Variance Analysis',
        'Inventory Tracking (Raw → WIP → Finished)',
        'Quality Control Integration',
        'Real-time Production Dashboards'
    ];

    return (
        <section className="manufacturing-bom-section">
            <div className="container">
                <div className="section-header">
                    <h2 className="section-title">
                        Manufacturing <span className="highlight-purple">& Production</span>
                    </h2>
                    <p className="section-subtitle">
                        Complete manufacturing management from raw materials to finished goods with 
                        integrated cost accounting and financial automation.
                    </p>
                </div>

                <div className="tab-navigation">
                    <button 
                        className={`tab-btn ${activeTab === 'bom' ? 'active' : ''}`}
                        onClick={() => setActiveTab('bom')}
                    >
                        <GitBranch size={20} />
                        Bill of Materials
                    </button>
                    <button 
                        className={`tab-btn ${activeTab === 'workflow' ? 'active' : ''}`}
                        onClick={() => setActiveTab('workflow')}
                    >
                        <Factory size={20} />
                        Manufacturing Workflow
                    </button>
                </div>

                {activeTab === 'bom' && (
                    <div className="bom-visualization">
                        <div className="bom-tree">
                            {bomLevels.map((level, idx) => (
                                <div key={idx} className={`bom-level level-${level.level}`}>
                                    <div className="level-header">
                                        <span className="level-badge">Level {level.level}</span>
                                        <h3>{level.name}</h3>
                                    </div>
                                    
                                    {level.level === 0 ? (
                                        <div className="bom-item finished-product">
                                            <div className="item-icon">
                                                <Package size={24} />
                                            </div>
                                            <div className="item-details">
                                                <h4>{level.item}</h4>
                                                <div className="item-meta">
                                                    <span>Qty: {level.quantity}</span>
                                                    <span className="cost">{level.cost}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bom-items-grid">
                                            {level.items.map((item, itemIdx) => (
                                                <div key={itemIdx} className="bom-item">
                                                    <div className="item-details">
                                                        <h4>{item.name}</h4>
                                                        <div className="item-meta">
                                                            <span>Qty: {item.qty}</span>
                                                            <span className="cost">{item.cost}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    
                                    {idx < bomLevels.length - 1 && (
                                        <div className="level-connector">
                                            <ArrowRight size={20} />
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        <div className="bom-summary">
                            <h3>Automated Cost Roll-up</h3>
                            <div className="cost-breakdown">
                                <div className="cost-item">
                                    <span>Raw Materials</span>
                                    <span className="amount">$520</span>
                                </div>
                                <div className="cost-item">
                                    <span>Sub-Assemblies</span>
                                    <span className="amount">$750</span>
                                </div>
                                <div className="cost-item">
                                    <span>Labor & Overhead</span>
                                    <span className="amount">$180</span>
                                </div>
                                <div className="cost-item total">
                                    <span>Total Product Cost</span>
                                    <span className="amount">$1,450</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'workflow' && (
                    <div className="workflow-visualization">
                        <div className="workflow-steps">
                            {workflowSteps.map((step, idx) => (
                                <React.Fragment key={idx}>
                                    <div className="workflow-step">
                                        <div className="step-icon">
                                            {step.icon}
                                        </div>
                                        <h3>{step.title}</h3>
                                        <p>{step.description}</p>
                                        <span className="step-status">{step.status}</span>
                                    </div>
                                    {idx < workflowSteps.length - 1 && (
                                        <div className="workflow-arrow">
                                            <ArrowRight size={24} />
                                        </div>
                                    )}
                                </React.Fragment>
                            ))}
                        </div>

                        <div className="integration-highlight">
                            <h3>Seamless Accounting Integration</h3>
                            <p>
                                Every manufacturing transaction automatically posts to your general ledger. 
                                Track inventory movements, work-in-progress, and finished goods with 
                                real-time financial impact.
                            </p>
                        </div>
                    </div>
                )}

                <div className="features-grid">
                    <h3>
                        Complete
                        <br />
                        Manufacturing
                        <br />
                        Suite
                    </h3>
                    <div className="features-list">
                        {features.map((feature, idx) => (
                            <div key={idx} className="feature-item">
                                <CheckCircle size={20} className="check-icon" />
                                <span>{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ManufacturingBOMSection;
