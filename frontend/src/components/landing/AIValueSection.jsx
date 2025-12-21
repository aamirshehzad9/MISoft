import React from 'react';
import { Clock, TrendingDown, Shield } from 'lucide-react';
import AnimatedCounter from '../shared/AnimatedCounter';
import SectionHeading from '../shared/SectionHeading';
import GlassCard from '../shared/GlassCard';
import './AIValueSection.css';

const AIValueSection = () => {
    const stats = [
        {
            icon: <Clock size={32} />,
            value: 85,
            suffix: '%',
            label: 'Time Saved on Reconciliation',
            description: 'Automated matching and exception handling'
        },
        {
            icon: <TrendingDown size={32} />,
            value: 92,
            suffix: '%',
            label: 'Error Reduction',
            description: 'AI-powered validation and anomaly detection'
        },
        {
            icon: <Shield size={32} />,
            value: 99,
            suffix: '%',
            label: 'Audit Confidence',
            description: 'Complete audit trail and compliance tracking'
        }
    ];

    return (
        <section className="ai-value-section">
            <div className="container">
                <SectionHeading
                    title="Measurable Business Impact"
                    subtitle="Real results from AI-powered accounting automation"
                />

                <div className="stats-grid">
                    {stats.map((stat, index) => (
                        <GlassCard key={index} className="stat-card" hover>
                            <div className="stat-icon">{stat.icon}</div>
                            <div className="stat-number">
                                <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                            </div>
                            <h3 className="stat-label">{stat.label}</h3>
                            <p className="stat-description">{stat.description}</p>
                        </GlassCard>
                    ))}
                </div>

                <div className="value-note">
                    <p>
                        <strong>Enterprise-Grade AI:</strong> Our machine learning models are trained
                        on millions of financial transactions to provide accurate, reliable automation.
                        All AI decisions include full audit trails and human oversight controls.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default AIValueSection;
