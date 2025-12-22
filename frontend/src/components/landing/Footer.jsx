import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Linkedin, Youtube } from 'lucide-react';
import { footerData } from '../../data/footer';
import logo from '../../assets/logo.png';
import './Footer.css';
import './sticky-header.css'; // Import shared logo styles

const Footer = () => {
    return (
        <footer className="w-full bg-black text-white pt-16 pb-8 border-t border-gray-800">
            <div className="container mx-auto px-4 md:px-8">
                {/* Main Footer Grid - 5 Columns */}
                <div className="footer-grid-5">
                    {/* Column 1: For business */}
                    <div>
                        <h4 className="text-white font-bold mb-4 text-sm uppercase tracking-wider">For business</h4>
                        <ul className="flex flex-col gap-2">
                            {footerData.links.business.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path} className="text-gray-300 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 2: Accountants & bookkeepers */}
                    <div>
                        <h4 className="text-white font-bold mb-4 text-sm uppercase tracking-wider">Accountants & bookkeepers</h4>
                        <ul className="flex flex-col gap-2">
                            {footerData.links.accountants.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path} className="text-gray-300 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 3: Features & Benefits */}
                    <div>
                        <h4 className="text-white font-bold mb-4 text-sm uppercase tracking-wider">Features & Benefits</h4>
                        <ul className="flex flex-col gap-2">
                            {footerData.links.features.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path} className="text-gray-300 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 4: Learn & support */}
                    <div>
                        <h4 className="text-white font-bold mb-4 text-sm uppercase tracking-wider">Learn & support</h4>
                        <ul className="flex flex-col gap-2">
                            {footerData.links.support.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path} className="text-gray-300 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 5: Tools & compliance */}
                    <div>
                        <h4 className="text-white font-bold mb-4 text-sm uppercase tracking-wider">Tools & compliance</h4>
                        <ul className="flex flex-col gap-2">
                            {footerData.links.tools.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path} className="text-gray-300 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Phone Number Section */}
                <div className="mb-8 pb-8 border-b border-gray-800">
                    <p className="text-gray-400 text-sm">
                        Call Sales: <a href={`tel:${footerData.contact.phone}`} className="text-white hover:text-[#15D46C] font-medium">{footerData.contact.phone}</a>
                    </p>
                </div>

                {/* Bottom Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    {/* Left: Logo + Country Selector */}
                    <div className="flex flex-col gap-4">
                        <Link to="/" className="flex items-center gap-3 text-decoration-none">
                            <img src={logo} alt="MISoft" className="brand-logo-crafted" />
                            <span className="text-xl font-bold tracking-tight text-white">MISoft</span>
                        </Link>
                        <div className="flex items-center gap-2">
                            <span className="text-2xl">🇺🇸</span>
                            <button className="text-gray-400 hover:text-white text-sm flex items-center gap-1">
                                Select Country
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    {/* Center: Legal Links */}
                    <div className="flex flex-wrap gap-4">
                        {footerData.legal.map((link, idx) => (
                            <Link key={idx} to={link.path} className="text-gray-400 hover:text-white text-sm text-decoration-none">
                                {link.label}
                            </Link>
                        ))}
                    </div>

                    {/* Right: Social Icons */}
                    <div className="flex items-center gap-3">
                        <a href={footerData.social.facebook || '#'} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                            <Facebook size={16} />
                        </a>
                        <a href={footerData.social.twitter} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                            <Twitter size={16} />
                        </a>
                        <a href={footerData.social.youtube} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                            <Youtube size={16} />
                        </a>
                        <a href={footerData.social.linkedin} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                            <Linkedin size={16} />
                        </a>
                    </div>
                </div>

                {/* Copyright Section */}
                <div className="mt-8 pt-6 border-t border-gray-800 text-xs text-gray-500">
                    <p className="mb-2">© 2025 GentleOmega Inc. All rights reserved.</p>
                    <p className="leading-relaxed">
                        Powered by <a href="https://gentleomegaai.space" className="text-gray-400 hover:text-white font-medium">GentleOmegaHoldings</a>.
                        MISoft, MIS, MITurboTax, MIProConnect, and Mint are registered trademarks of GentleOmega Inc.
                        Terms and conditions, features, support, and service options subject to change without notice.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
