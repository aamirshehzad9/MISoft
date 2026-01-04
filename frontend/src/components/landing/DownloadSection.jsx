import React from 'react';
import { Database, Package, Download, CheckCircle, AlertCircle, Server, HardDrive, Cloud } from 'lucide-react';
import './DownloadSection.css';

const DownloadSection = () => {
    const packages = [
        {
            id: 'sqlite',
            name: 'SQLite Package',
            icon: <HardDrive size={40} />,
            description: 'Perfect for small to medium businesses',
            version: 'v1.0.0',
            size: '45 MB',
            badge: 'Recommended',
            badgeColor: 'blue',
            features: [
                'Zero configuration required',
                'Single-file database',
                'Up to 100 users',
                'Ideal for local deployment',
                'No server setup needed',
                'Built-in backup tools'
            ],
            requirements: {
                os: 'Windows 10+, macOS 10.15+, Linux',
                ram: '4 GB RAM minimum',
                storage: '500 MB free space',
                python: 'Python 3.14+'
            },
            downloadUrl: '#sqlite-download'
        },
        {
            id: 'docker',
            name: 'Docker Package',
            icon: <Package size={40} />,
            description: 'Enterprise-ready containerized deployment',
            version: 'v1.0.0',
            size: '120 MB',
            badge: 'Enterprise',
            badgeColor: 'purple',
            features: [
                'Full PostgreSQL database',
                'Unlimited users',
                'Auto-scaling support',
                'Cloud-ready deployment',
                'Kubernetes compatible',
                'Production-grade security'
            ],
            requirements: {
                os: 'Docker Desktop 4.0+',
                ram: '8 GB RAM minimum',
                storage: '2 GB free space',
                docker: 'Docker Engine 20.10+'
            },
            downloadUrl: '#docker-download'
        }
    ];

    const installSteps = {
        sqlite: [
            'Download the SQLite package',
            'Extract to your preferred directory',
            'Run setup.py to initialize database',
            'Start the application with start.ps1',
            'Access at http://localhost:5173'
        ],
        docker: [
            'Download the Docker package',
            'Extract docker-compose.yml',
            'Run: docker-compose up -d',
            'Wait for containers to start (~2 min)',
            'Access at http://localhost:5173'
        ]
    };

    return (
        <section className="download-section">
            <div className="container">
                <div className="section-header">
                    <div className="database-badge">
                        <Database size={20} />
                        <span>Installation Packages</span>
                    </div>
                    <h2 className="section-title">
                        Choose Your <span className="highlight-blue">Deployment</span> Package
                    </h2>
                    <p className="section-subtitle">
                        Download the package that best fits your business needs. Both options include 
                        the full MISoft platform with AI capabilities.
                    </p>
                </div>

                <div className="packages-grid">
                    {packages.map((pkg) => (
                        <div key={pkg.id} className="package-card">
                            <div className="package-header">
                                <div className="package-icon">
                                    {pkg.icon}
                                </div>
                                <div className="package-info">
                                    <div className="package-title-row">
                                        <h3>{pkg.name}</h3>
                                        <span className={`package-badge ${pkg.badgeColor}`}>
                                            {pkg.badge}
                                        </span>
                                    </div>
                                    <p className="package-description">{pkg.description}</p>
                                </div>
                            </div>

                            <div className="package-meta">
                                <div className="meta-item">
                                    <span className="meta-label">Version</span>
                                    <span className="meta-value">{pkg.version}</span>
                                </div>
                                <div className="meta-item">
                                    <span className="meta-label">Size</span>
                                    <span className="meta-value">{pkg.size}</span>
                                </div>
                            </div>

                            <div className="package-features">
                                <h4>Features</h4>
                                <ul>
                                    {pkg.features.map((feature, idx) => (
                                        <li key={idx}>
                                            <CheckCircle size={16} />
                                            <span>{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="package-requirements">
                                <h4>System Requirements</h4>
                                <div className="requirements-list">
                                    {Object.entries(pkg.requirements).map(([key, value]) => (
                                        <div key={key} className="requirement-item">
                                            <AlertCircle size={14} />
                                            <span>{value}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <button className="download-btn">
                                <Download size={20} />
                                Download {pkg.name}
                            </button>
                        </div>
                    ))}
                </div>

                <div className="installation-guides">
                    <h3 className="guides-title">Quick Installation Guides</h3>
                    <div className="guides-grid">
                        <div className="guide-card">
                            <div className="guide-header">
                                <HardDrive size={28} />
                                <h4>SQLite Installation</h4>
                            </div>
                            <ol className="installation-steps">
                                {installSteps.sqlite.map((step, idx) => (
                                    <li key={idx}>{step}</li>
                                ))}
                            </ol>
                            <div className="guide-time">
                                <span>⏱️ Setup Time: ~5 minutes</span>
                            </div>
                        </div>

                        <div className="guide-card">
                            <div className="guide-header">
                                <Package size={28} />
                                <h4>Docker Installation</h4>
                            </div>
                            <ol className="installation-steps">
                                {installSteps.docker.map((step, idx) => (
                                    <li key={idx}>{step}</li>
                                ))}
                            </ol>
                            <div className="guide-time">
                                <span>⏱️ Setup Time: ~10 minutes</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="deployment-comparison">
                    <h3>Not Sure Which Package to Choose?</h3>
                    <div className="comparison-grid">
                        <div className="comparison-card">
                            <Server size={32} className="comparison-icon" />
                            <h4>Choose SQLite if:</h4>
                            <ul>
                                <li>You have less than 100 users</li>
                                <li>You want quick, simple setup</li>
                                <li>You prefer local deployment</li>
                                <li>You don't need cloud scaling</li>
                            </ul>
                        </div>
                        <div className="comparison-card">
                            <Cloud size={32} className="comparison-icon" />
                            <h4>Choose Docker if:</h4>
                            <ul>
                                <li>You have 100+ users</li>
                                <li>You need enterprise features</li>
                                <li>You want cloud deployment</li>
                                <li>You require auto-scaling</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default DownloadSection;
