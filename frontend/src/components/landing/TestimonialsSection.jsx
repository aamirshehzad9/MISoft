import React, { useState } from 'react';
import { Star, Quote, ChevronLeft, ChevronRight, Building2, TrendingUp } from 'lucide-react';
import './TestimonialsSection.css';

const TestimonialsSection = () => {
    const [currentTestimonial, setCurrentTestimonial] = useState(0);

    const testimonials = [
        {
            name: 'Sarah Chen',
            role: 'CFO',
            company: 'TechVision Inc.',
            image: '👩‍💼',
            rating: 5,
            text: 'MISoft transformed our financial operations. The AI-powered reconciliation alone saves us 40 hours per month. IFRS compliance is now automated, and our audit process is seamless.',
            metrics: { saved: '40hrs/month', accuracy: '99.8%' }
        },
        {
            name: 'Michael Rodriguez',
            role: 'Finance Director',
            company: 'Global Manufacturing Ltd.',
            image: '👨‍💼',
            rating: 5,
            text: 'The manufacturing ERP integration is outstanding. Real-time cost tracking from raw materials to finished goods has given us unprecedented visibility into our operations.',
            metrics: { saved: '35hrs/month', accuracy: '99.5%' }
        },
        {
            name: 'Aisha Patel',
            role: 'Controller',
            company: 'Retail Solutions Group',
            image: '👩‍💼',
            rating: 5,
            text: 'Multi-currency support is flawless. We operate in 25 countries, and MISoft handles all our consolidation and revaluation automatically. The hybrid deployment gave us complete control.',
            metrics: { saved: '50hrs/month', accuracy: '100%' }
        },
        {
            name: 'James Thompson',
            role: 'CEO',
            company: 'StartupHub Ventures',
            image: '👨‍💼',
            rating: 5,
            text: 'As a startup, we needed enterprise-grade accounting without enterprise costs. The free local deployment option was perfect, and we scaled to cloud seamlessly as we grew.',
            metrics: { saved: '$2,400/year', accuracy: '99.9%' }
        }
    ];

    const clientLogos = [
        { name: 'TechVision', icon: '🚀' },
        { name: 'Global Mfg', icon: '🏭' },
        { name: 'Retail Solutions', icon: '🛒' },
        { name: 'StartupHub', icon: '💡' },
        { name: 'Finance Pro', icon: '💼' },
        { name: 'Enterprise Co', icon: '🏢' }
    ];

    const successMetrics = [
        { value: '500+', label: 'Enterprise Clients', icon: <Building2 size={24} /> },
        { value: '99.8%', label: 'Accuracy Rate', icon: <Star size={24} /> },
        { value: '10M+', label: 'Transactions Processed', icon: <TrendingUp size={24} /> },
        { value: '4.9/5', label: 'Average Rating', icon: <Star size={24} /> }
    ];

    const nextTestimonial = () => {
        setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    };

    const prevTestimonial = () => {
        setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length);
    };

    const current = testimonials[currentTestimonial];

    return (
        <section className="testimonials-section">
            <div className="container">
                <div className="section-header">
                    <h2 className="section-title">
                        Trusted by <span className="highlight-cyan">Finance Leaders</span>
                    </h2>
                    <p className="section-subtitle">
                        Join hundreds of companies that have transformed their financial operations with MISoft
                    </p>
                </div>

                <div className="testimonial-showcase">
                    <div className="testimonial-card">
                        <div className="quote-icon">
                            <Quote size={48} />
                        </div>
                        
                        <div className="testimonial-content">
                            <div className="rating">
                                {[...Array(current.rating)].map((_, i) => (
                                    <Star key={i} size={20} fill="#fbbf24" color="#fbbf24" />
                                ))}
                            </div>
                            
                            <p className="testimonial-text">{current.text}</p>
                            
                            <div className="testimonial-metrics">
                                <div className="metric">
                                    <span className="metric-value">{current.metrics.saved}</span>
                                    <span className="metric-label">Time Saved</span>
                                </div>
                                <div className="metric">
                                    <span className="metric-value">{current.metrics.accuracy}</span>
                                    <span className="metric-label">Accuracy</span>
                                </div>
                            </div>
                        </div>

                        <div className="testimonial-author">
                            <div className="author-avatar">{current.image}</div>
                            <div className="author-info">
                                <h4>{current.name}</h4>
                                <p>{current.role}</p>
                                <p className="company">{current.company}</p>
                            </div>
                        </div>

                        <div className="testimonial-navigation">
                            <button className="nav-btn" onClick={prevTestimonial}>
                                <ChevronLeft size={24} />
                            </button>
                            <div className="testimonial-dots">
                                {testimonials.map((_, idx) => (
                                    <button
                                        key={idx}
                                        className={`dot ${idx === currentTestimonial ? 'active' : ''}`}
                                        onClick={() => setCurrentTestimonial(idx)}
                                    />
                                ))}
                            </div>
                            <button className="nav-btn" onClick={nextTestimonial}>
                                <ChevronRight size={24} />
                            </button>
                        </div>
                    </div>
                </div>

                <div className="client-logos">
                    <h3>Trusted by Leading Organizations</h3>
                    <div className="logos-grid">
                        {clientLogos.map((client, idx) => (
                            <div key={idx} className="logo-card">
                                <span className="logo-icon">{client.icon}</span>
                                <span className="logo-name">{client.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="success-metrics">
                    {successMetrics.map((metric, idx) => (
                        <div key={idx} className="success-metric">
                            <div className="metric-icon">{metric.icon}</div>
                            <div className="metric-value">{metric.value}</div>
                            <div className="metric-label">{metric.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default TestimonialsSection;
