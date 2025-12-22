import React from 'react';
import { ShieldCheck, Cloud, Globe } from 'lucide-react';
import HeroBackground from './HeroBackground';
import DashboardPreview from './DashboardPreview';

const HeroSection = () => {
    return (
        <section className="relative w-full min-h-screen pt-36 pb-24 overflow-hidden flex items-center">
            {/* Background Layer - Forensic "White Base + Peaceful Particles" */}
            <div className="absolute inset-0 z-0 bg-white">
                <HeroBackground />
            </div>

            <div className="container relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                {/* Left Content (Dominant 60%) */}
                <div
                    className="lg:col-span-7 flex flex-col gap-8 pr-0 lg:pr-12"
                >
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary/5 rounded-full border border-brand-primary/10 w-fit">
                        <span className="w-2 h-2 rounded-full bg-[#15D46C] animate-pulse"></span>
                        <span className="text-sm font-semibold text-brand-primary tracking-wide uppercase">New: AI Auto-Reconciliation</span>
                    </div>

                    {/* Headline - Forensic Typography (QuickBooks Scale) */}
                    <h1 className="text-6xl lg:text-[5rem] font-bold text-gray-900 leading-[1.05] tracking-tight">
                        Precision in <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary to-brand-secondary">
                            Data.
                        </span> <br />
                        Intelligence in Strategy.
                    </h1>

                    <p className="text-xl text-gray-600 max-w-2xl leading-relaxed font-medium">
                        The AI-first accounting platform for manufacturing & retail.
                        IFRS-compliant, hybrid deployment, and enterprise-grade security.
                    </p>

                    {/* Trust Signals */}
                    <div className="flex flex-wrap gap-6 text-sm text-gray-500 font-semibold my-2">
                        <div className="flex items-center gap-2"><ShieldCheck size={18} className="text-[#15D46C]" /> SOC 2 Type II</div>
                        <div className="flex items-center gap-2"><Cloud size={18} className="text-[#15D46C]" /> 99.99% Uptime</div>
                        <div className="flex items-center gap-2"><Globe size={18} className="text-[#15D46C]" /> Multi-Currency</div>
                    </div>

                    {/* CTAs - Enterprise Size */}
                    <div className="flex items-center gap-4 mt-2">
                        <a href="/pricing" className="bg-[#15D46C] text-white text-lg font-bold px-10 py-4 rounded-full shadow-lg shadow-green-500/20 hover:shadow-green-500/40 hover:bg-[#12b85e] transition-all transform hover:-translate-y-0.5">
                            See Plans & Pricing
                        </a>
                        <button className="px-10 py-4 rounded-full border-2 border-brand-primary/20 text-brand-primary font-bold hover:bg-brand-primary/5 transition-colors">
                            Watch Demo
                        </button>
                    </div>

                    <p className="text-sm text-gray-400 font-medium">
                        No credit card required • 14-day free trial • Cancel anytime
                    </p>
                </div>

                {/* Right Content - Animated Dashboard (40%) */}
                <div className="hidden lg:block lg:col-span-5 relative z-20">
                    <DashboardPreview />
                </div>
            </div>
        </section>
    );
};

export default HeroSection;
