import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, Search, User, ChevronDown } from 'lucide-react';
import MegaMenu from './MegaMenu';
import CountrySelector from './CountrySelector';
import logo from '../../assets/logo.png';
import './sticky-header.css';

const StickyHeader = () => {
    const [scrolled, setScrolled] = useState(false);
    const [activeMenu, setActiveMenu] = useState(null); // 'business' | 'accountants' | null
    const [countryModalOpen, setCountryModalOpen] = useState(false);
    const [selectedCountry, setSelectedCountry] = useState('PK'); // Default Pakistan
    const [hoverTimeout, setHoverTimeout] = useState(null);

    // Interaction Handlers (Hover Intent)
    const handleMouseEnter = (menu) => {
        if (hoverTimeout) clearTimeout(hoverTimeout);
        setActiveMenu(menu);
    };

    const handleMouseLeave = () => {
        const timeout = setTimeout(() => {
            setActiveMenu(null);
        }, 300); // 300ms grace period
        setHoverTimeout(timeout);
    };

    const handleMenuEnter = () => {
        if (hoverTimeout) clearTimeout(hoverTimeout);
    };

    // Scroll Logic for Transformation
    useEffect(() => {
        const handleScroll = () => {
            const offset = window.scrollY;
            if (offset > 50) {
                setScrolled(true);
            } else {
                setScrolled(false);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <>
            <header className={`sticky-header ${scrolled ? 'scrolled' : ''}`}>
                <div className="container" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    {/* Left Group: Logo + Main Navigation */}
                    <div className="flex flex-row items-center gap-10">
                        {/* Logo Section - Keeping 40px aligned WITH MARGIN */}
                        <Link to="/" className="brand-logo-container mr-12" style={{ marginRight: '3rem' }}>
                            <img src={logo} alt="MISoft Logo" className="brand-logo-crafted" />
                            <span className="brand-text">MISoft</span>
                        </Link>

                        {/* Navigation - Desktop (Forensic Structure: Left-Aligned) */}
                        <nav className="hidden md:flex flex-row items-center gap-10" onMouseLeave={handleMouseLeave}>
                            <div className="relative h-full flex items-center">
                                <button
                                    className="nav-link"
                                    onMouseEnter={() => handleMouseEnter('business')}
                                    onClick={() => setActiveMenu(activeMenu === 'business' ? null : 'business')}
                                >
                                    For Business <ChevronDown size={14} className={`transition-transform duration-300 ${activeMenu === 'business' ? 'rotate-180' : ''}`} />
                                </button>
                            </div>

                            <div className="relative h-full flex items-center">
                                <button
                                    className="nav-link"
                                    onMouseEnter={() => handleMouseEnter('accountants')}
                                    onClick={() => setActiveMenu(activeMenu === 'accountants' ? null : 'accountants')}
                                >
                                    Accountants <ChevronDown size={14} className={`transition-transform duration-300 ${activeMenu === 'accountants' ? 'rotate-180' : ''}`} />
                                </button>
                            </div>

                            <Link to="/pricing" className="nav-link text-decoration-none">
                                Pricing
                            </Link>
                            <Link to="/resources" className="nav-link text-decoration-none">
                                Learn & Support <ChevronDown size={14} className="opacity-70" />
                            </Link>
                        </nav>
                    </div>

                    {/* Right Group: Utility + CTA */}
                    <div className="flex items-center gap-4">
                        {/* Country Selector */}
                        <button
                            className="country-selector-btn text-white"
                            onClick={() => setCountryModalOpen(true)}
                        >
                            <GlobeIcon country={selectedCountry} />
                            <span className="text-sm font-medium">{selectedCountry}</span>
                        </button>

                        {/* Search Icon */}
                        <button className="hidden lg:flex items-center gap-1 bg-transparent border-none cursor-pointer text-white hover:text-brand-accent-green transition-colors">
                            <Search size={18} />
                        </button>

                        {/* Login Dropdown */}
                        <div className="login-dropdown-wrapper hidden md:block group">
                            <Link to="/login" className="nav-link font-medium flex items-center gap-1 text-decoration-none">
                                Sign In <ChevronDown size={14} />
                            </Link>
                            <div className="glass-card login-dropdown-menu p-4 w-48 shadow-xl">
                                <Link to="/login" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none font-medium">MISoft Online</Link>
                                <Link to="/login-payroll" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none font-medium">Payroll</Link>
                                <Link to="/login-pro" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none font-medium">ProAdvisors</Link>
                            </div>
                        </div>

                        {/* CTA */}
                        <Link
                            to="/register"
                            className="bg-[#15D46C] text-white font-bold rounded-full hover:bg-[#12b85e] transition-all shadow-lg"
                            style={{
                                padding: scrolled ? '8px 20px' : '10px 24px',
                                fontSize: '0.95rem'
                            }}
                        >
                            Start Free Trial
                        </Link>

                        {/* Mobile Menu Toggle */}
                        <button className="md:hidden bg-transparent border-none text-white">
                            <Menu size={24} />
                        </button>
                    </div>
                </div>
            </header>

            {/* Mega Menu Component - Fixed Position below header */}
            <div
                className={`fixed left-0 w-full z-[990] transition-all duration-300 ease-in-out ${activeMenu ? 'opacity-100 translate-y-0 visible' : 'opacity-0 -translate-y-4 invisible'}`}
                style={{ top: scrolled ? '72px' : '90px' }}
                onMouseEnter={() => { handleMenuEnter(); if (matchMedia('(min-width: 768px)').matches && activeMenu) setActiveMenu(activeMenu); }}
                onMouseLeave={handleMouseLeave}
            >
                <MegaMenu
                    isOpen={!!activeMenu}
                    activeMenu={activeMenu}
                    onMouseEnter={handleMenuEnter}
                    onMouseLeave={handleMouseLeave}
                />
            </div>

            {/* Country Selecor Modal */}
            {countryModalOpen && (
                <CountrySelector onClose={() => setCountryModalOpen(false)} />
            )}
        </>
    );
};

// Helper for Flag Icon
const GlobeIcon = ({ country }) => {
    const flags = { 'PK': '🇵🇰', 'US': '🇺🇸', 'UK': '🇬🇧' };
    return <span style={{ fontSize: '1.2rem' }}>{flags[country] || '🌐'}</span>;
};

export default StickyHeader;
