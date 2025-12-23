import React from 'react';
import { ShieldCheck, Cloud, Globe } from 'lucide-react';
import AdvancedHeroBackground from './AdvancedHeroBackground';
import AIAccountingSlideshow from './AIAccountingSlideshow';
import './HeroSection.css';

const HeroSection = () => {
    return (
        <section className="relative w-full min-h-[90vh] max-h-[90vh] overflow-hidden flex items-center justify-center" style={{ paddingTop: '120px', paddingBottom: '80px', background: 'transparent', position: 'relative' }}>
            {/* Advanced Animated Background */}
            <div className="absolute inset-0">
                <AdvancedHeroBackground />
            </div>

            <div className="hero-container-responsive container mx-auto px-4 lg:px-8 max-w-[1400px] relative z-10 flex flex-col lg:flex-row gap-12 items-center">
                {/* Left Content (55% on desktop) */}
                <div
                    className="hero-text-column flex flex-col gap-6 pr-0 lg:pr-8 relative z-50"
                    style={{ flexBasis: '55%', flexGrow: 0, flexShrink: 1 }}
                >
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full border border-white/20 w-fit backdrop-blur-sm">
                        <span className="w-2 h-2 rounded-full bg-[#667eea] animate-pulse"></span>
                        <span className="text-sm font-semibold text-white tracking-wide uppercase">New: AI Auto-Reconciliation</span>
                    </div>

                    {/* Headline - Resized for Better Balance */}
                    <h1
                        className="text-6xl lg:text-7xl font-bold text-white leading-[1.1] tracking-tight"
                        style={{ fontSize: '5rem', lineHeight: '1.1', color: 'white' }}
                    >
                        Precision in <br />
                        <span className="text-[#667eea]">
                            Data.
                        </span> <br />
                        Intelligence in Strategy.
                    </h1>

                    <p
                        className="text-xl text-gray-300 max-w-2xl leading-relaxed font-medium"
                        style={{ fontSize: '1.25rem' }}
                    >
                        The AI-first accounting platform for manufacturing & retail.
                        IFRS-compliant, hybrid deployment, and enterprise-grade security.
                    </p>

                    {/* Trust Signals */}
                    <div className="flex flex-wrap gap-6 text-sm text-gray-400 font-semibold my-2">
                        <div className="flex items-center gap-2"><ShieldCheck size={18} className="text-[#667eea]" /> SOC 2 Type II</div>
                        <div className="flex items-center gap-2"><Cloud size={18} className="text-[#667eea]" /> 99.99% Uptime</div>
                        <div className="flex items-center gap-2"><Globe size={18} className="text-[#667eea]" /> Multi-Currency</div>
                    </div>

                    {/* CTAs - Larger Size */}
                    <div className="flex items-center gap-4 mt-2">
                        <a href="/pricing" className="bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white text-xl font-bold px-14 py-5 rounded-full shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 hover:scale-105 transition-all transform">
                            See Plans & Pricing
                        </a>
                        <button className="px-14 py-5 rounded-full border-2 border-white/20 text-white text-xl font-bold hover:bg-white/10 hover:border-[#667eea] transition-all">
                            Watch Demo
                        </button>
                    </div>

                    <p className="text-sm text-gray-500 font-medium">
                        No credit card required • 14-day free trial • Cancel anytime
                    </p>
                </div>

                {/* Right Content - AI Accounting Slideshow (45% on desktop) */}
                <div className="hero-animation-column hidden lg:block relative z-20" style={{ flexBasis: '45%', flexGrow: 0, flexShrink: 1 }}>
                    <AIAccountingSlideshow />
                </div>
            </div>
        </section>
    );
};

export default HeroSection;
