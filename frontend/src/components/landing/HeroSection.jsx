import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import GlassCard from '../shared/GlassCard';
import './HeroSection.css';

const HeroSection = () => {
    return (
        <section className="hero-section">
            <div className="hero-particles"></div>

            <div className="container hero-content">
                <div className="hero-text animate-fade-in">
                    <h1 className="hero-title">
                        Enterprise <span className="text-gradient">AI Accounting</span>
                        <br />
                        & Finance Platform
                    </h1>

                    <p className="hero-subtitle">
                        IFRS-Compliant | Hybrid Deployment | Manufacturing ERP
                        <br />
                        <span className="neon-text">Powered by Artificial Intelligence</span>
                    </p>

                    <div className="hero-cta">
                        <Link to="/register" className="btn btn-primary btn-lg">
                            <Sparkles size={20} />
                            Start Free Trial
                            <ArrowRight size={20} />
                        </Link>

                        <Link to="/login" className="btn btn-secondary btn-lg">
                            Login to Dashboard
                        </Link>
                    </div>

                    <div className="hero-features">
                        <div className="feature-badge">
                            <span className="badge-icon">✓</span>
                            Full Data Ownership
                        </div>
                        <div className="feature-badge">
                            <span className="badge-icon">✓</span>
                            IFRS Compliant
                        </div>
                        <div className="feature-badge">
                            <span className="badge-icon">✓</span>
                            AI-Powered
                        </div>
                    </div>
                </div>

                <div className="hero-visual animate-slide-right">
                    <GlassCard className="dashboard-preview" glow>
                        <div className="preview-header">
                            <div className="preview-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                            <div className="preview-title">MISoft Dashboard</div>
                        </div>

                        <div className="preview-content">
                            <div className="preview-stat">
                                <div className="stat-label">Total Revenue</div>
                                <div className="stat-value text-gradient">$2.4M</div>
                                <div className="stat-change positive">+12.5%</div>
                            </div>

                            <div className="preview-stat">
                                <div className="stat-label">Active Invoices</div>
                                <div className="stat-value">1,247</div>
                                <div className="stat-change positive">+8.3%</div>
                            </div>

                            <div className="preview-chart">
                                <div className="chart-bar" style={{ height: '60%' }}></div>
                                <div className="chart-bar" style={{ height: '80%' }}></div>
                                <div className="chart-bar" style={{ height: '45%' }}></div>
                                <div className="chart-bar" style={{ height: '90%' }}></div>
                                <div className="chart-bar" style={{ height: '70%' }}></div>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </section>
    );
};

export default HeroSection;
