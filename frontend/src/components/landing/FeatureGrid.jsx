import React from 'react';
import { FileCheck, Globe, Factory, Brain } from 'lucide-react';
import GlassCard from '../shared/GlassCard';
import SectionHeading from '../shared/SectionHeading';
import FeatureCard from './FeatureCard';
import './FeatureGrid.css';

const FeatureGrid = () => {
    const features = [
        {
            icon: <FileCheck size={32} />,
            title: 'IFRS Compliance',
            description: 'Full International Financial Reporting Standards compliance built-in. Automated journal entries, multi-currency support, and audit-ready reports.',
            highlights: ['Automated IFRS 15 & 16', 'Audit Trail', 'Financial Statements']
        },
        {
            icon: <Globe size={32} />,
            title: 'Multi-Currency',
            description: 'Handle transactions in 150+ currencies with real-time exchange rates. Automatic revaluation and consolidated reporting across all entities.',
            highlights: ['150+ Currencies', 'Auto Revaluation', 'Consolidated Reports']
        },
        {
            icon: <Factory size={32} />,
            title: 'Manufacturing ERP',
            description: 'Complete manufacturing management from raw materials to finished goods. Inventory tracking, production planning, and cost accounting integrated.',
            highlights: ['Inventory Control', 'Production Planning', 'Cost Accounting']
        },
        {
            icon: <Brain size={32} />,
            title: 'AI Engine',
            description: 'Automated reconciliation, fraud detection, and financial forecasting. Machine learning adapts to your business patterns for smarter insights.',
            highlights: ['Auto Reconciliation', 'Fraud Detection', 'Forecasting']
        }
    ];

    return (
        <section className="feature-grid-section">
            <div className="container">
                <SectionHeading
                    title="Enterprise Accounting Features"
                    subtitle="Professional-grade tools designed for accuracy, compliance, and control"
                />

                <div className="features-grid">
                    {features.map((feature, index) => (
                        <FeatureCard key={index} {...feature} />
                    ))}
                </div>
            </div>
        </section>
    );
};

export default FeatureGrid;
