import React from 'react';
import { Zap, Shield, TrendingUp, Brain, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import './AIAddonsMarketplace.css';

const AIAddonsMarketplace = () => {
    const addons = [
        {
            icon: <Zap size={32} />,
            name: 'AI Reconciliation',
            tagline: 'Autonomous bank reconciliation',
            price: '$19',
            period: '/month',
            description: 'Automatically match thousands of transactions with 99.9% accuracy. Reduce reconciliation time from hours to minutes.',
            features: [
                'Automatic transaction matching',
                'Smart pattern recognition',
                'Multi-bank support',
                'Real-time reconciliation',
                'Variance analysis'
            ],
            popular: true,
            color: 'purple'
        },
        {
            icon: <Shield size={32} />,
            name: 'AI Fraud Detection',
            tagline: 'Real-time fraud prevention',
            price: '$29',
            period: '/month',
            description: 'Machine learning algorithms detect anomalies and suspicious patterns before they become problems.',
            features: [
                'Real-time anomaly detection',
                'Pattern analysis',
                'Risk scoring',
                'Alert notifications',
                'Compliance reporting'
            ],
            popular: false,
            color: 'cyan'
        },
        {
            icon: <TrendingUp size={32} />,
            name: 'AI Forecasting',
            tagline: 'Predictive financial analytics',
            price: '$24',
            period: '/month',
            description: 'Advanced forecasting models predict cash flow, revenue, and expenses with unprecedented accuracy.',
            features: [
                'Cash flow predictions',
                'Revenue forecasting',
                'Expense modeling',
                'Scenario analysis',
                'Trend identification'
            ],
            popular: false,
            color: 'purple'
        },
        {
            icon: <Brain size={32} />,
            name: 'AI Smart Vouchers',
            tagline: 'Intelligent journal entries',
            price: '$15',
            period: '/month',
            description: 'AI suggests optimal journal entries based on transaction patterns and historical data.',
            features: [
                'Smart entry suggestions',
                'Auto-categorization',
                'Learning from history',
                'Compliance checks',
                'Audit trail'
            ],
            popular: false,
            color: 'cyan'
        }
    ];

    return (
        <section className="ai-addons-marketplace">
            <div className="container">
                <div className="section-header">
                    <div className="sparkle-icon">
                        <Sparkles size={40} />
                    </div>
                    <h2 className="section-title">
                        AI Add-ons <span className="highlight-purple">Marketplace</span>
                    </h2>
                    <p className="section-subtitle">
                        Supercharge your accounting with premium AI-powered features. 
                        Mix and match add-ons to create your perfect financial automation suite.
                    </p>
                </div>

                <div className="addons-grid">
                    {addons.map((addon, idx) => (
                        <div key={idx} className={`addon-card ${addon.color} ${addon.popular ? 'popular' : ''}`}>
                            {addon.popular && (
                                <div className="popular-badge">
                                    <Sparkles size={16} />
                                    Most Popular
                                </div>
                            )}
                            
                            <div className="addon-icon">
                                {addon.icon}
                            </div>
                            
                            <h3 className="addon-name">{addon.name}</h3>
                            <p className="addon-tagline">{addon.tagline}</p>
                            
                            <div className="addon-pricing">
                                <span className="price">{addon.price}</span>
                                <span className="period">{addon.period}</span>
                            </div>
                            
                            <p className="addon-description">{addon.description}</p>
                            
                            <div className="addon-features">
                                {addon.features.map((feature, featureIdx) => (
                                    <div key={featureIdx} className="feature-item">
                                        <CheckCircle size={16} className="check-icon" />
                                        <span>{feature}</span>
                                    </div>
                                ))}
                            </div>
                            
                            <button className="addon-cta">
                                Add to Plan
                                <ArrowRight size={18} />
                            </button>
                        </div>
                    ))}
                </div>

                <div className="marketplace-cta">
                    <div className="cta-content">
                        <h3>Explore the Full Marketplace</h3>
                        <p>
                            Discover 20+ AI-powered add-ons designed to automate every aspect 
                            of your financial operations. From tax automation to expense management, 
                            we have the tools you need.
                        </p>
                        <button className="browse-btn">
                            Browse All Add-ons
                            <ArrowRight size={20} />
                        </button>
                    </div>
                    <div className="cta-stats">
                        <div className="stat">
                            <span className="stat-value">20+</span>
                            <span className="stat-label">AI Add-ons</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">$15-$49</span>
                            <span className="stat-label">Price Range</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">Mix & Match</span>
                            <span className="stat-label">Flexible Plans</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default AIAddonsMarketplace;
