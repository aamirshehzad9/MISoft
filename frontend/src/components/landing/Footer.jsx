import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Linkedin, Youtube } from 'lucide-react';
import { footerData } from '../../data/footer';
import logo from '../../assets/logo.png';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer-professional">
            <div className="footer-container">
                {/* Main Footer Grid - 5 Columns */}
                <div className="footer-grid-5">
                    {/* Column 1: For business */}
                    <div className="footer-column">
                        <h4>For business</h4>
                        <ul>
                            {footerData.links.business.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 2: Accountants & bookkeepers */}
                    <div className="footer-column">
                        <h4>Accountants & bookkeepers</h4>
                        <ul>
                            {footerData.links.accountants.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 3: Features & Benefits */}
                    <div className="footer-column">
                        <h4>Features & Benefits</h4>
                        <ul>
                            {footerData.links.features.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 4: Learn & support */}
                    <div className="footer-column">
                        <h4>Learn & support</h4>
                        <ul>
                            {footerData.links.support.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Column 5: Tools & compliance */}
                    <div className="footer-column">
                        <h4>Tools & compliance</h4>
                        <ul>
                            {footerData.links.tools.map((link, idx) => (
                                <li key={idx}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Phone Number Section */}
                <div className="footer-phone-section">
                    <p>
                        Call Sales: <a href={`tel:${footerData.contact.phone}`}>{footerData.contact.phone}</a>
                    </p>
                </div>

                {/* Bottom Section - Three Part Layout */}
                <div className="footer-bottom">
                    {/* Left: Logo + Country Selector */}
                    <div className="footer-bottom-left">
                        <Link to="/" className="footer-logo-link">
                            <img src={logo} alt="MISoft" className="footer-logo-img" />
                            <span className="footer-logo-text">MISoft</span>
                        </Link>
                        <div className="footer-country-selector">
                            <span className="country-flag"></span>
                            <button className="country-select-btn">
                                Select Country
                                <svg className="chevron-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    {/* Center: Legal Links */}
                    <div className="footer-bottom-center">
                        {footerData.legal.map((link, idx) => (
                            <Link key={idx} to={link.path}>{link.label}</Link>
                        ))}
                    </div>

                    {/* Right: Social Icons */}
                    <div className="footer-bottom-right">
                        <a href={footerData.social.facebook || '#'} className="social-icon">
                            <Facebook size={16} />
                        </a>
                        <a href={footerData.social.twitter} className="social-icon">
                            <Twitter size={16} />
                        </a>
                        <a href={footerData.social.youtube} className="social-icon">
                            <Youtube size={16} />
                        </a>
                        <a href={footerData.social.linkedin} className="social-icon">
                            <Linkedin size={16} />
                        </a>
                    </div>
                </div>

                {/* Copyright Section */}
                <div className="footer-copyright">
                    <p> 2025 GentleOmega Inc. All rights reserved.</p>
                    <p className="footer-powered">
                        Powered by <a href="https://gentleomegaai.space">GentleOmegaHoldings</a>.
                        MISoft, MIS, MITurboTax, MIProConnect, and Mint are registered trademarks of GentleOmega Inc.
                        Terms and conditions, features, support, and service options subject to change without notice.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
