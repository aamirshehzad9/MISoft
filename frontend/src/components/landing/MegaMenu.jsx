import React from 'react';
import { Link } from 'react-router-dom';
import {
    CreditCard, BarChart2, Briefcase, Globe,
    Layers, Zap, Users, Shield,
    FileText, Settings, Database, Cloud, MessageCircle
} from 'lucide-react';
import './mega-menu.css';

const MegaMenu = ({ isOpen, onMouseEnter, onMouseLeave }) => {
    return (
        <div
            className={`mega-menu-container ${isOpen ? 'active' : ''}`}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            <div className="mega-menu-grid-visual">
                {/* Left Side: Dense Link Lists (2 Columns) */}
                <div className="menu-links-section">
                    <div className="menu-column">
                        <div className="persona-header">PLANS & PRICING</div>
                        <p className="menu-subtitle">Find which plan best suits your business.</p>

                        <Link to="/pricing" className="menu-item-compact">
                            <span className="new-badge">NEW</span>
                            <div className="menu-text-group">
                                <span className="menu-item-title">QuickBooks Online Advanced</span>
                                <span className="menu-item-description">For larger businesses with complex needs.</span>
                            </div>
                        </Link>

                        <div className="menu-spacer"></div>

                        <div className="persona-header">HELPFUL RESOURCES</div>
                        <Link to="/resources" className="menu-item-compact">
                            <span className="menu-item-title">Resources for small business owners</span>
                        </Link>
                        <Link to="/advisor" className="menu-item-compact">
                            <span className="menu-item-title">Find an Advisor</span>
                            <span className="menu-item-description">Find a QuickBooks Certified bookkeeper.</span>
                        </Link>
                    </div>

                    <div className="menu-column">
                        <Link to="/features/bank-feeds" className="menu-item-iconless">Bank Feeds</Link>
                        <Link to="/features/cloud" className="menu-item-iconless">Cloud Accounting</Link>
                        <Link to="/features/invoicing" className="menu-item-iconless">Invoicing</Link>
                        <Link to="/features/projects" className="menu-item-iconless">Project Profitability</Link>
                        <Link to="/features/reports" className="menu-item-iconless">Accounting Reports</Link>
                        <Link to="/features/inventory" className="menu-item-iconless">Inventory Management</Link>
                        <div className="menu-divider"></div>
                        <Link to="/features/migration" className="menu-item-iconless">Data Migration</Link>
                        <Link to="/features/gst" className="menu-item-iconless">GST & VAT Tracking</Link>
                        <Link to="/features/expenses" className="menu-item-iconless">Expense Tracker</Link>
                        <Link to="/mobile-app" className="menu-item-iconless">Mobile Accounting App</Link>
                        <Link to="/apps" className="menu-item-iconless">Connect Your Apps</Link>
                        <Link to="/features" className="menu-item-bold">See all features</Link>
                    </div>
                </div>

                {/* Right Side: Visual Cards (2 Columns) */}
                <div className="menu-visuals-section">
                    {/* Visual Card 1: Invoice Generator / Promo */}
                    <div className="visual-card-wrapper">
                        <div className="visual-card-image bg-gray-100 h-32 rounded-t-lg mb-3 flex items-center justify-center">
                            {/* Placeholder for the 'Guy with Laptop' image from screenshot */}
                            <Users size={48} className="text-gray-300" />
                        </div>
                        <h3 className="visual-card-title">Free Invoice Generator</h3>
                        <p className="visual-card-text">Our free online invoice generator makes business invoicing a breeze.</p>
                    </div>

                    {/* Visual Card 2: WhatsApp Community */}
                    <div className="visual-card-wrapper bg-dark-blue text-white">
                        <div className="visual-card-content p-6 rounded-lg bg-[#25D366] text-white h-full flex flex-col justify-between">
                            <div className="icon-circle bg-white text-[#25D366] w-12 h-12 rounded-full flex items-center justify-center mb-4">
                                <MessageCircle size={24} />
                            </div>
                            <div>
                                <h3 className="visual-card-title text-white">WhatsApp Community</h3>
                                <p className="visual-card-text text-white/90 mb-0">Join 5,000+ Finance Pros</p>
                                <p className="visual-card-text text-white/80 text-xs mt-1">Get Tips & Free Templates</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MegaMenu;
