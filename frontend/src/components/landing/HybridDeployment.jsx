import React, { useState } from 'react';
import { Cloud, HardDrive, Shield, Zap, Lock } from 'lucide-react';
import GlassCard from '../shared/GlassCard';
import SectionHeading from '../shared/SectionHeading';
import './HybridDeployment.css';

const HybridDeployment = () => {
    const [activeTab, setActiveTab] = useState('cloud');

    const cloudFeatures = [
        {
            icon: <Cloud size={24} />,
            title: 'Cloud Flexibility',
            description: 'Access your accounting data from anywhere, anytime. Automatic updates and backups included.'
        },
        {
            icon: <Shield size={24} />,
            title: 'Enterprise Security',
            description: 'Bank-level encryption, SOC 2 compliance, and 99.99% uptime SLA for your financial data.'
        },
        {
            icon: <Zap size={24} />,
            title: 'Instant Scalability',
            description: 'Scale resources automatically as your business grows. No infrastructure management required.'
        }
    ];

    const localFeatures = [
        {
            icon: <HardDrive size={24} />,
            title: 'Full Data Ownership',
            description: 'Your financial data stays on your infrastructure. Complete control over data location and access.'
        },
        {
            icon: <Lock size={24} />,
            title: 'Network Isolation',
            description: 'Run entirely on your local network. No internet dependency for core accounting operations.'
        },
        {
            icon: <Shield size={24} />,
            title: 'Compliance Ready',
            description: 'Meet strict data residency requirements. Ideal for regulated industries and government sectors.'
        }
    ];

    const features = activeTab === 'cloud' ? cloudFeatures : localFeatures;

    return (
        <section className="hybrid-deployment-section">
            <div className="container">
                <SectionHeading
                    title="Hybrid Deployment Options"
                    subtitle="Choose the deployment model that fits your business needs and compliance requirements"
                />

                <div className="deployment-toggle">
                    <button
                        className={`toggle-btn ${activeTab === 'cloud' ? 'active' : ''}`}
                        onClick={() => setActiveTab('cloud')}
                    >
                        <Cloud size={20} />
                        Cloud Deployment
                    </button>
                    <button
                        className={`toggle-btn ${activeTab === 'local' ? 'active' : ''}`}
                        onClick={() => setActiveTab('local')}
                    >
                        <HardDrive size={20} />
                        Local Deployment
                    </button>
                </div>

                <div className="features-grid">
                    {features.map((feature, index) => (
                        <GlassCard key={index} className="feature-card" hover>
                            <div className="feature-icon">{feature.icon}</div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </GlassCard>
                    ))}
                </div>

                <div className="deployment-note">
                    <p>
                        <strong>Hybrid Approach:</strong> Start with cloud deployment for quick setup,
                        then migrate to local infrastructure as your needs evolve. Both options support
                        the same feature set and IFRS compliance standards.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default HybridDeployment;
