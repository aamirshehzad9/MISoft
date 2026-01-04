import React, { useState } from 'react';
import { Building2, Calendar, FileText, CheckCircle, ArrowRight, Clock, Zap } from 'lucide-react';
import './OnboardingPreview.css';

const OnboardingPreview = () => {
    const [activeStep, setActiveStep] = useState(0);

    const steps = [
        {
            number: 1,
            icon: <Building2 size={32} />,
            title: 'Company Setup',
            description: 'Enter your company details and preferences',
            features: [
                'Company name and address',
                'Industry selection',
                'Currency preferences',
                'Tax registration details'
            ],
            time: '2 min'
        },
        {
            number: 2,
            icon: <Calendar size={32} />,
            title: 'Fiscal Year',
            description: 'Configure your accounting periods',
            features: [
                'Fiscal year start date',
                'Accounting periods',
                'Reporting calendar',
                'Period lock settings'
            ],
            time: '1 min'
        },
        {
            number: 3,
            icon: <FileText size={32} />,
            title: 'Chart of Accounts',
            description: 'Choose from industry-specific templates',
            features: [
                'Pre-built COA templates',
                'Industry-specific accounts',
                'Customizable structure',
                'IFRS compliant setup'
            ],
            time: '2 min'
        }
    ];

    return (
        <section className="onboarding-preview">
            <div className="container">
                <div className="section-header">
                    <div className="time-badge">
                        <Clock size={20} />
                        <span>5 Minutes to Get Started</span>
                    </div>
                    <h2 className="section-title">
                        Setup in <span className="highlight-green">Minutes</span>, Not Days
                    </h2>
                    <p className="section-subtitle">
                        Our intelligent setup wizard guides you through a simple 3-step process. 
                        No accounting expertise required – we'll handle the complexity for you.
                    </p>
                </div>

                <div className="wizard-container">
                    <div className="wizard-steps">
                        {steps.map((step, idx) => (
                            <div 
                                key={idx} 
                                className={`wizard-step ${activeStep === idx ? 'active' : ''} ${activeStep > idx ? 'completed' : ''}`}
                                onClick={() => setActiveStep(idx)}
                            >
                                <div className="step-number">
                                    {activeStep > idx ? (
                                        <CheckCircle size={24} />
                                    ) : (
                                        <span>{step.number}</span>
                                    )}
                                </div>
                                <div className="step-info">
                                    <h4>{step.title}</h4>
                                    <span className="step-time">{step.time}</span>
                                </div>
                                {idx < steps.length - 1 && (
                                    <div className="step-connector"></div>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="wizard-content">
                        <div className="step-icon">
                            {steps[activeStep].icon}
                        </div>
                        <h3>{steps[activeStep].title}</h3>
                        <p className="step-description">{steps[activeStep].description}</p>
                        
                        <div className="step-features">
                            {steps[activeStep].features.map((feature, idx) => (
                                <div key={idx} className="feature-item">
                                    <CheckCircle size={18} className="check-icon" />
                                    <span>{feature}</span>
                                </div>
                            ))}
                        </div>

                        <div className="step-navigation">
                            {activeStep > 0 && (
                                <button 
                                    className="nav-btn secondary"
                                    onClick={() => setActiveStep(activeStep - 1)}
                                >
                                    Previous
                                </button>
                            )}
                            {activeStep < steps.length - 1 ? (
                                <button 
                                    className="nav-btn primary"
                                    onClick={() => setActiveStep(activeStep + 1)}
                                >
                                    Next Step
                                    <ArrowRight size={18} />
                                </button>
                            ) : (
                                <button className="nav-btn primary complete">
                                    Complete Setup
                                    <CheckCircle size={18} />
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                <div className="onboarding-benefits">
                    <div className="benefit-card">
                        <div className="benefit-icon">
                            <Zap size={28} />
                        </div>
                        <h4>5-Minute Setup</h4>
                        <p>Get your accounting system ready in the time it takes to make coffee</p>
                    </div>
                    <div className="benefit-card">
                        <div className="benefit-icon">
                            <FileText size={28} />
                        </div>
                        <h4>Pre-Built Templates</h4>
                        <p>Industry-specific COA templates save hours of manual configuration</p>
                    </div>
                    <div className="benefit-card">
                        <div className="benefit-icon">
                            <CheckCircle size={28} />
                        </div>
                        <h4>IFRS Compliant</h4>
                        <p>All templates follow international accounting standards out of the box</p>
                    </div>
                </div>

                <div className="onboarding-cta">
                    <h3>Ready to Get Started?</h3>
                    <p>Join thousands of businesses that set up their accounting in minutes</p>
                    <button className="get-started-btn">
                        Start Free Setup
                        <ArrowRight size={20} />
                    </button>
                </div>
            </div>
        </section>
    );
};

export default OnboardingPreview;
