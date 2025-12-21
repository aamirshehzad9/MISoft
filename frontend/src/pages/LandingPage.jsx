import React from 'react';
import { Helmet } from 'react-helmet-async';
import Header from '../components/landing/Header';
import HeroSection from '../components/landing/HeroSection';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <>
            <Helmet>
                <title>MISoft - Enterprise AI Accounting & Finance Platform | IFRS Compliant ERP</title>
                <meta name="description" content="World-class IFRS-compliant AI accounting and finance platform. Hybrid deployment, manufacturing ERP, multi-currency support. Compete with QuickBooks Enterprise and SAP Business One." />
                <meta name="keywords" content="accounting software, IFRS ERP, AI accounting, manufacturing ERP, QuickBooks alternative, SAP alternative, cloud accounting, hybrid deployment" />

                {/* Open Graph */}
                <meta property="og:title" content="MISoft - Enterprise AI Accounting Platform" />
                <meta property="og:description" content="IFRS-compliant AI accounting and finance platform with hybrid deployment" />
                <meta property="og:type" content="website" />
                <meta property="og:url" content="https://misoft.gentleomegaai.space/" />

                {/* Twitter Card */}
                <meta name="twitter:card" content="summary_large_image" />
                <meta name="twitter:title" content="MISoft - Enterprise AI Accounting Platform" />
                <meta name="twitter:description" content="IFRS-compliant AI accounting with hybrid deployment" />
            </Helmet>

            <div className="landing-page">
                <Header />

                <main className="landing-main">
                    <HeroSection />

                    {/* Placeholder for future sections */}
                    <section id="features" className="section">
                        <div className="container text-center">
                            <h2 className="text-gradient">Core Features</h2>
                            <p className="text-secondary">Coming soon: IFRS Compliance, Multi-Currency, Manufacturing, AI Engine</p>
                        </div>
                    </section>

                    <section id="pricing" className="section">
                        <div className="container text-center">
                            <h2 className="text-gradient">Pricing Plans</h2>
                            <p className="text-secondary">Coming soon: Free, Cloud Basic, Cloud Premium, Enterprise</p>
                        </div>
                    </section>

                    <section id="faq" className="section">
                        <div className="container text-center">
                            <h2 className="text-gradient">Frequently Asked Questions</h2>
                            <p className="text-secondary">Coming soon: Data ownership, Security, Compliance</p>
                        </div>
                    </section>
                </main>

                <footer className="landing-footer">
                    <div className="container">
                        <p className="text-center text-secondary">
                            MISoft is powered by <a href="https://gentleomegaai.space/" target="_blank" rel="noopener noreferrer" className="text-gradient">GentleOmegaAI</a>
                        </p>
                        <p className="text-center text-muted">
                            © 2025 MISoft. All Rights Reserved.
                        </p>
                    </div>
                </footer>
            </div>
        </>
    );
};

export default LandingPage;
