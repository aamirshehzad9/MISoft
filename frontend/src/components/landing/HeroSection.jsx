import React from 'react';
import { ShieldCheck, Cloud, Globe } from 'lucide-react';
import HeroBackground from './HeroBackground';
import DashboardPreview from './DashboardPreview';

const HeroSection = () => {
    return (
        <section className="relative w-full min-h-screen pt-[120px] pb-20 overflow-hidden flex items-center">
            {/* Background Layer - Forensic "White Base + Peaceful Particles" */}
            <div className="absolute inset-0 z-0 bg-white">
                <HeroBackground />
            </div>

            <div className="container relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                {/* Left Content */}
                <div
                    className="flex flex-col gap-6"
                >
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary/5 rounded-full border border-brand-primary/10 w-fit">
                        <span className="w-2 h-2 rounded-full bg-brand-accent-green animate-pulse"></span>
                        <span className="text-sm font-semibold text-brand-primary tracking-wide uppercase">New: AI Auto-Reconciliation</span>
                    </div>

                    {/* Headline - Forensic Typography (QuickBooks Style) */}
                    <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-[1.1] tracking-tight">
                        The Enterprise <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary to-brand-secondary">
                            AI Accounting Platform
                        </span>
                    </h1>

                    <p className="text-lg text-gray-600 max-w-lg leading-relaxed">
                        Hybrid Cloud & Local deployment. IFRS-Compliant.
                        Designed for manufacturing, retail, and service industries
                        that demand more than just bookkeeping.
                    </p>

                    {/* Trust Signals */}
                    <div className="flex flex-wrap gap-4 text-sm text-gray-500 font-medium">
                        <div className="flex items-center gap-1"><ShieldCheck size={16} className="text-brand-primary" /> SOC 2 Type II</div>
                        <div className="flex items-center gap-1"><Cloud size={16} className="text-brand-primary" /> 99.99% Uptime</div>
                        <div className="flex items-center gap-1"><Globe size={16} className="text-brand-primary" /> Multi-Currency</div>
                    </div>

                    {/* CTAs */}
                    <div className="flex items-center gap-4 mt-4">
                        <a href="/register" className="btn-primary text-lg px-8 py-3 shadow-lg shadow-brand-primary/20 hover:shadow-brand-primary/40 transition-shadow">
                            Start Free Trial
                        </a>
                        <button className="px-8 py-3 rounded-lg border border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition-colors bg-white/50 backdrop-blur-sm">
                            Watch Demo
                        </button>
                    </div>

                    <p className="text-sm text-gray-400 mt-2">
                        No credit card required • 14-day free trial • Cancel anytime
                    </p>
                </div>

                {/* Right Content - Animated Dashboard */}
                <div className="hidden lg:block relative z-20">
                    <DashboardPreview />
                </div>
            </div>
        </section>
    );
};

export default HeroSection;
