import React, { useState } from 'react';
import { Cloud, HardDrive } from 'lucide-react';
import GlassCard from '../shared/GlassCard';
import SectionHeading from '../shared/SectionHeading';
import './HybridDeployment.css';

// Import deployment images
import cloudFlexibility from '../../assets/deployment/cloud_flexibility.png';
import enterpriseSecurity from '../../assets/deployment/enterprise_security.png';
import instantScalability from '../../assets/deployment/instant_scalability.png';
import autoBackup from '../../assets/deployment/auto_backup.png';
import dataOwnership from '../../assets/deployment/data_ownership.png';
import networkIsolation from '../../assets/deployment/network_isolation.png';
import complianceReady from '../../assets/deployment/compliance_ready.png';
import costEffective from '../../assets/deployment/cost_effective.png';

const HybridDeployment = () => {
    const [activeTab, setActiveTab] = useState('cloud');

    const cloudFeatures = [
        {
            image: cloudFlexibility,
            title: 'Cloud Flexibility',
            description: 'Access your accounting data from anywhere, anytime. Automatic updates and backups included.'
        },
        {
            image: enterpriseSecurity,
            title: 'Enterprise Security',
            description: 'Bank-level encryption, SOC 2 compliance, and 99.99% uptime SLA for your financial data.'
        },
        {
            image: instantScalability,
            title: 'Instant Scalability',
            description: 'Scale resources automatically as your business grows. No infrastructure management required.'
        },
        {
            image: autoBackup,
            title: 'Automated Backups',
            description: 'Daily automated backups with point-in-time recovery. Never lose your financial data.'
        }
    ];

    const localFeatures = [
        {
            image: dataOwnership,
            title: 'Full Data Ownership',
            description: 'Your financial data stays on your infrastructure. Complete control over data location and access.'
        },
        {
            image: networkIsolation,
            title: 'Network Isolation',
            description: 'Run entirely on your local network. No internet dependency for core accounting operations.'
        },
        {
            image: complianceReady,
            title: 'Compliance Ready',
            description: 'Meet strict data residency requirements. Ideal for regulated industries and government sectors.'
        },
        {
            image: costEffective,
            title: 'Cost Effective',
            description: 'No monthly subscription fees. One-time setup with complete ownership of your infrastructure.'
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

                <div className="features-grid-4x4">
                    {features.map((feature, index) => (
                        <GlassCard key={index} className="feature-card" hover>
                            <div className="feature-image-container">
                                <img src={feature.image} alt={feature.title} className="feature-image" />
                            </div>
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
