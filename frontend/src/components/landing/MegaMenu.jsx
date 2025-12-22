import React from 'react';
import { Link } from 'react-router-dom';
import {
    CreditCard, BarChart2, Briefcase, Globe,
    Layers, Zap, Users, Shield,
    FileText, Settings, Database, Cloud
} from 'lucide-react';
import './mega-menu.css';

const MegaMenu = ({ isOpen }) => {
    return (
        <div className={`mega-menu-container ${isOpen ? 'active' : ''}`}>
            <div className="mega-menu-grid">
                {/* Column 1: Core Features */}
                <div className="persona-column">
                    <div className="persona-header">MISoft FEATURES</div>
                    <Link to="/features/accounting" className="menu-item">
                        <FileText size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Accounting & Finance</span>
                            <span className="menu-item-description">General Ledger, AP/AR</span>
                        </div>
                    </Link>
                    <Link to="/features/inventory" className="menu-item">
                        <Database size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Inventory Management</span>
                            <span className="menu-item-description">Multi-warehouse tracking</span>
                        </div>
                    </Link>
                    <Link to="/features/projects" className="menu-item">
                        <Briefcase size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Project Costing</span>
                            <span className="menu-item-description">Real-time profitability</span>
                        </div>
                    </Link>
                </div>

                {/* Column 2: Solutions by Industry */}
                <div className="persona-column">
                    <div className="persona-header">SOLUTIONS</div>
                    <Link to="/solutions/manufacturing" className="menu-item">
                        <Settings size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Manufacturing</span>
                            <span className="menu-item-description">BOM, Production Planning</span>
                        </div>
                    </Link>
                    <Link to="/solutions/retail" className="menu-item">
                        <Users size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Retail & Commerce</span>
                            <span className="menu-item-description">POS Integration</span>
                        </div>
                    </Link>
                    <Link to="/solutions/global" className="menu-item">
                        <Globe size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Global Business</span>
                            <span className="menu-item-description">Multi-entity & Currency</span>
                        </div>
                    </Link>
                </div>

                {/* Column 3: Platform & Tech */}
                <div className="persona-column">
                    <div className="persona-header">PLATFORM</div>
                    <Link to="/hybrid" className="menu-item">
                        <Cloud size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Hybrid Deployment</span>
                            <span className="menu-item-description">Cloud + Local Sync</span>
                        </div>
                    </Link>
                    <Link to="/security" className="menu-item">
                        <Shield size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Enterprise Security</span>
                            <span className="menu-item-description">SOC 2 Type II</span>
                        </div>
                    </Link>
                </div>

                {/* Column 4: Resources & Pricing */}
                <div className="persona-column">
                    <div className="persona-header">GROWTH</div>
                    <Link to="/pricing" className="menu-item">
                        <CreditCard size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Plans & Pricing</span>
                            <span className="menu-item-description">Scalable tiers</span>
                        </div>
                    </Link>
                    <Link to="/resources" className="menu-item">
                        <Layers size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Resource Center</span>
                            <span className="menu-item-description">Guides & Support</span>
                        </div>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default MegaMenu;
