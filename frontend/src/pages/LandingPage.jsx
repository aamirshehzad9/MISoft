import React from 'react';
import { Helmet } from 'react-helmet-async';
import StickyHeader from '../components/landing/StickyHeader';
import HeroSection from '../components/landing/HeroSection';
import HybridDeployment from '../components/landing/HybridDeployment';
import FeatureGrid from '../components/landing/FeatureGrid';
import AIValueSection from '../components/landing/AIValueSection';
import PricingSection from '../components/landing/PricingSection';
import FAQSection from '../components/landing/FAQSection';
import AIExcellenceShowcase from '../components/landing/AIExcellenceShowcase';
import ManufacturingBOMSection from '../components/landing/ManufacturingBOMSection';
import TestimonialsSection from '../components/landing/TestimonialsSection';
import AIAddonsMarketplace from '../components/landing/AIAddonsMarketplace';
import OnboardingPreview from '../components/landing/OnboardingPreview';
import DownloadSection from '../components/landing/DownloadSection';
import Footer from '../components/landing/Footer';
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
                <StickyHeader />

                <main className="landing-main">
                    <HeroSection />
                    <HybridDeployment />
                    <FeatureGrid />
                    <ManufacturingBOMSection />
                    <AIValueSection />
                    <AIExcellenceShowcase />
                    <AIAddonsMarketplace />
                    <PricingSection />
                    <TestimonialsSection />
                    <OnboardingPreview />
                    <DownloadSection />
                    <FAQSection />
                </main>

                <Footer />
            </div>
        </>
    );
};

export default LandingPage;
