import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, CheckCircle, Zap } from 'lucide-react';
import GlassCard from '../shared/GlassCard';
import './HeroSection.css';

const HeroSection = () => {
    return (
        <section className="hero-section">
            <div className="container hero-content">
                <div className="hero-text">
                    <h1 className="hero-title">
                        Enterprise AI Accounting
                        <br />
                        & Finance Platform
                    </h1>

                    <p className="hero-subtitle">
                        IFRS-Compliant | Hybrid Deployment | Manufacturing ERP
                    </p>

                    <div className="hero-cta">
                        <Link to="/register" className="btn-hero btn-primary">
                            <span>Start Free Trial</span>
                            <ArrowRight size={20} />
                        </Link>

                        <Link to="/login" className="btn-hero btn-secondary">
                            Login to Dashboard
                        </Link>
                    </div>

                    <div className="hero-features">
                        <div className="feature-badge">
                            <Shield size={16} />
                            <span>Full Data Ownership</span>
                        </div>
                        <div className="feature-badge">
                            <CheckCircle size={16} />
                            <span>IFRS Compliant</span>
                        </div>
                        <div className="feature-badge">
                            <Zap size={16} />
                            <span>AI-Powered</span>
                        </div>
                    </div>
                </div>

                <div className="hero-visual">
                    <GlassCard className="dashboard-preview">
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
                                <div className="stat-value">$2.4M</div>
                                <div className="stat-change">+12.5%</div>
                            </div>

                            <div className="preview-stat">
                                <div className="stat-label">Active Invoices</div>
                                <div className="stat-value">1,247</div>
                                <div className="stat-change">+8.3%</div>
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
