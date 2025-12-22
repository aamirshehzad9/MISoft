import React from 'react';
import { Link } from 'react-router-dom';
import {
    CreditCard, BarChart2, Briefcase, Globe,
    Layers, Zap, Users, Shield,
    FileText, Settings, Database, Cloud, MessageCircle
} from 'lucide-react';
import './mega-menu.css';

const MegaMenu = ({ isOpen, activeMenu, onMouseEnter, onMouseLeave }) => {
    return (
        <div
            className={`mega-menu-container ${isOpen ? 'active' : ''}`}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            <div className="mega-menu-grid-visual">
                {/* Dynamically Render Content Based on Active Menu */}
                {activeMenu === 'accountants' ? (
                    /* Accountants Content Structure */
                    <>
                        <div className="menu-links-section">
                            <div className="menu-column">
                                <div className="persona-header">MANAGE YOUR CLIENTS</div>
                                <Link to="/accountants/client-accounting" className="menu-item-iconless">Online Accountant</Link>
                                <Link to="/accountants/payroll" className="menu-item-iconless">Payroll for Accountants</Link>
                                <Link to="/accountants/pro-tax" className="menu-item-iconless">Pro Tax</Link>
                                <div className="menu-divider"></div>
                                <div className="persona-header h-mt-4">GROW YOUR PRACTICE</div>
                                <Link to="/accountants/proadvisor" className="menu-item-iconless">ProAdvisor Program</Link>
                                <Link to="/accountants/directory" className="menu-item-iconless">Find-a-ProAdvisor Directory</Link>
                                <Link to="/accountants/marketing" className="menu-item-iconless">Marketing Hub</Link>
                            </div>
                            <div className="menu-column">
                                <div className="persona-header">TRAINING & CERTIFICATION</div>
                                <Link to="/accountants/training" className="menu-item-iconless">ProAdvisor Certification</Link>
                                <Link to="/accountants/webinars" className="menu-item-iconless">Webinars & Events</Link>
                                <Link to="/accountants/tutorials" className="menu-item-iconless">Video Tutorials</Link>
                                <div className="menu-divider"></div>
                                <div className="persona-header h-mt-4">RESOURCES</div>
                                <Link to="/accountants/blog" className="menu-item-iconless">Firm of the Future Blog</Link>
                                <Link to="/accountants/support" className="menu-item-iconless">Accountant Support</Link>
                            </div>
                        </div>
                        {/* Right Side: Visuals for Accountants */}
                        <div className="menu-visuals-section">
                            <div className="visual-card-wrapper">
                                <div className="visual-card-image bg-gray-100 h-32 rounded-t-lg mb-3 flex items-center justify-center">
                                    <Briefcase size={48} className="text-gray-300" />
                                </div>
                                <h3 className="visual-card-title">ProAdvisor Program</h3>
                                <p className="visual-card-text">Join the program to grow your skills and your practice.</p>
                            </div>
                            <div className="visual-card-wrapper bg-dark-blue text-white">
                                <div className="visual-card-content p-6 rounded-lg bg-[#0077C5] text-white h-full flex flex-col justify-between">
                                    <div className="icon-circle bg-white text-[#0077C5] w-12 h-12 rounded-full flex items-center justify-center mb-4">
                                        <Users size={24} />
                                    </div>
                                    <div>
                                        <h3 className="visual-card-title text-white">Sign up for free</h3>
                                        <p className="visual-card-text text-white/90 mb-0">QuickBooks Online Accountant</p>
                                        <p className="visual-card-text text-white/80 text-xs mt-1">Manage all your clients in one place.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </>
                ) : (
                    /* Default: For Business Content */
                    <>
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

                        {/* Right Side: Visual Cards (For Business) */}
                        <div className="menu-visuals-section">
                            <div className="visual-card-wrapper">
                                <div className="visual-card-image bg-gray-100 h-32 rounded-t-lg mb-3 flex items-center justify-center">
                                    <Users size={48} className="text-gray-300" />
                                </div>
                                <h3 className="visual-card-title">Free Invoice Generator</h3>
                                <p className="visual-card-text">Our free online invoice generator makes business invoicing a breeze.</p>
                            </div>
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
                    </>
                )}
            </div>
        </div>
    );
};

export default MegaMenu;
