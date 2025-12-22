import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, Search, User, ChevronDown } from 'lucide-react';
import MegaMenu from './MegaMenu';
import CountrySelector from './CountrySelector';
import logo from '../../assets/logo.png';
import './sticky-header.css';

const StickyHeader = () => {
    const [scrolled, setScrolled] = useState(false);
    const [megaMenuOpen, setMegaMenuOpen] = useState(false);
    const [countryModalOpen, setCountryModalOpen] = useState(false);
    const [selectedCountry, setSelectedCountry] = useState('PK'); // Default Pakistan

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
                    {/* Logo Section */}
                    <Link to="/" className="flex items-center gap-2 text-decoration-none">
                        <img src={logo} alt="MISoft Logo" className="h-10 w-auto object-contain" />
                    </Link>

                    {/* Navigation - Desktop (Mega Menu Trigger) */}
                    <nav className="hidden md:flex items-center gap-8">
                        <button
                            className="nav-link bg-transparent border-none cursor-pointer flex items-center gap-1"
                            onMouseEnter={() => setMegaMenuOpen(true)}
                            onClick={() => setMegaMenuOpen(!megaMenuOpen)}
                        >
                            Products & Features <ChevronDown size={14} />
                        </button>
                        <Link to="/resources" className="nav-link text-decoration-none">Resources</Link>
                        <Link to="/pricing" className="nav-link text-decoration-none">Pricing</Link>
                    </nav>

                    {/* Right Actions */}
                    <div className="flex items-center gap-4">
                        {/* Country Selector */}
                        <button
                            className="country-selector-btn"
                            onClick={() => setCountryModalOpen(true)}
                        >
                            <GlobeIcon country={selectedCountry} />
                            <span className="text-sm font-medium">{selectedCountry}</span>
                        </button>

                        {/* Search Icon */}
                        <button className="bg-transparent border-none cursor-pointer p-2 text-gray-500 hover:text-brand-primary transition-colors">
                            <Search size={20} />
                        </button>

                        {/* Login Dropdown */}
                        <div className="login-dropdown-wrapper hidden md:block">
                            <Link to="/login" className="nav-link font-medium flex items-center gap-1 text-decoration-none">
                                Sign In <ChevronDown size={14} />
                            </Link>
                            <div className="glass-card login-dropdown-menu p-4 w-48 shadow-xl">
                                <Link to="/login" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none">QuickBooks Online</Link>
                                <Link to="/login-payroll" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none">Payroll</Link>
                                <Link to="/login-pro" className="block py-2 px-3 hover:bg-gray-50 rounded text-sm text-gray-700 text-decoration-none">ProAdvisors</Link>
                            </div>
                        </div>

                        {/* CTA */}
                        <Link
                            to="/register"
                            className="btn-primary"
                            style={{
                                padding: scrolled ? '8px 16px' : '10px 24px',
                                fontSize: scrolled ? '0.9rem' : '1rem'
                            }}
                        >
                            Start Free Trial
                        </Link>

                        {/* Mobile Menu Toggle */}
                        <button className="md:hidden bg-transparent border-none text-gray-700">
                            <Menu size={24} />
                        </button>
                    </div>
                </div>
            </header>

            {/* Mega Menu Component - Tied to Header State */}
            <div onMouseLeave={() => setMegaMenuOpen(false)}>
                <MegaMenu isOpen={megaMenuOpen} />
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
