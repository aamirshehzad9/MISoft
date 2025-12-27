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
                                <div className="persona-header">FOR BUSINESS</div>
                                
                                {/* Section 1: Plans & Pricing */}
                                <div className="menu-section">
                                    <Link to="/pricing" className="menu-section-heading">Plans & Pricing</Link>
                                    <p className="menu-section-content">Find which plan best suits your business.</p>
                                </div>
                                
                                {/* Section 2: MISoft Advanced Online */}
                                <div className="menu-section">
                                    <span className="new-badge">NEW</span>
                                    <Link to="/advanced" className="menu-section-heading">MISoft Advanced Online</Link>
                                    <p className="menu-section-content">For larger businesses with complex requirements and needs.</p>
                                </div>
                                
                                {/* Section 3: Helpful Resources */}
                                <div className="menu-section">
                                    <Link to="/resources" className="menu-section-heading">Helpful Resources</Link>
                                    <p className="menu-section-content">Resources for retailers, small medium enterprise owners.</p>
                                </div>
                                
                                {/* Section 4: Find an Advisor */}
                                <div className="menu-section">
                                    <Link to="/advisor" className="menu-section-heading">Find an Advisor</Link>
                                    <p className="menu-section-content">Find a MISoft Certified bookkeeper or accountant online</p>
                                </div>
                            </div>


                            <div className="menu-column features-grid">
                                <div className="persona-header">FEATURES</div>
                                
                                {/* Column 1 - 6 items */}
                                <Link to="/features/bank-feeds" className="menu-item-with-icon">
                                    <Database size={16} className="feature-icon" />
                                    <span>Bank Feeds</span>
                                </Link>
                                <Link to="/features/cloud" className="menu-item-with-icon">
                                    <Cloud size={16} className="feature-icon" />
                                    <span>Cloud Accounting</span>
                                </Link>
                                <Link to="/features/ai-invoicing" className="menu-item-with-icon">
                                    <FileText size={16} className="feature-icon" />
                                    <span>AI Invoicing</span>
                                </Link>
                                <Link to="/features/projects" className="menu-item-with-icon">
                                    <BarChart2 size={16} className="feature-icon" />
                                    <span>Project Profitability</span>
                                </Link>
                                <Link to="/features/reports" className="menu-item-with-icon">
                                    <Layers size={16} className="feature-icon" />
                                    <span>Accounting Reports</span>
                                </Link>
                                <Link to="/features/inventory" className="menu-item-with-icon">
                                    <Briefcase size={16} className="feature-icon" />
                                    <span>Inventory Management</span>
                                </Link>
                                
                                {/* Column 2 - 6 items + See all features */}
                                <Link to="/features/ai-reconciliation" className="menu-item-with-icon">
                                    <Zap size={16} className="feature-icon" />
                                    <span>AI Auto Reconciliation</span>
                                </Link>
                                <Link to="/features/ai-accountant" className="menu-item-with-icon">
                                    <Users size={16} className="feature-icon" />
                                    <span>AI Virtual Accountant</span>
                                </Link>
                                <Link to="/features/migration" className="menu-item-with-icon">
                                    <Database size={16} className="feature-icon" />
                                    <span>Data Migration</span>
                                </Link>
                                <Link to="/features/gst" className="menu-item-with-icon">
                                    <CreditCard size={16} className="feature-icon" />
                                    <span>GST & VAT Tracking</span>
                                </Link>
                                <Link to="/features/expenses" className="menu-item-with-icon">
                                    <CreditCard size={16} className="feature-icon" />
                                    <span>Expense Tracker</span>
                                </Link>
                                <Link to="/mobile-app" className="menu-item-with-icon">
                                    <Globe size={16} className="feature-icon" />
                                    <span>Mobile Accounting App</span>
                                </Link>
                                <Link to="/features" className="menu-item-bold">See all features</Link>
                            </div>
                        </div>

                        {/* Right Side: Visual Cards (For Business) */}
                        <div className="menu-visuals-section">
                            <div className="visual-card-wrapper">
                                <div className="visual-card-image rounded-t-lg mb-3 overflow-hidden" style={{height: '160px'}}>
                                    <img 
                                        src="/images/invoice-generator-mockup.png" 
                                        alt="AI Invoice Generator Preview"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <h3 className="visual-card-title" style={{fontWeight: 400}}>Our online AI invoice generator makes business invoicing an ease.</h3>
                            </div>
                            <div className="visual-card-wrapper">
                                <div className="visual-card-image rounded-lg overflow-hidden" style={{height: '160px'}}>
                                    <img 
                                        src="/images/whatsapp-contact.jpg" 
                                        alt="Contact Us on WhatsApp"
                                        className="w-full h-full object-cover"
                                    />
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
