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
                {/* Persona 1: Simple Start (Solopreneurs) */}
                <div className="persona-column">
                    <div className="persona-header">SIMPLE START</div>
                    <Link to="/features/invoicing" className="menu-item">
                        <FileText size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Invoicing & Quotes</span>
                            <span className="menu-item-description">Professional templates</span>
                        </div>
                    </Link>
                    <Link to="/features/expenses" className="menu-item">
                        <CreditCard size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Expense Tracking</span>
                            <span className="menu-item-description">Snap receipts instantly</span>
                        </div>
                    </Link>
                </div>

                {/* Persona 2: Essentials (Small Business) */}
                <div className="persona-column">
                    <div className="persona-header">ESSENTIALS</div>
                    <Link to="/features/multi-currency" className="menu-item">
                        <Globe size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Multi-Currency</span>
                            <span className="menu-item-description">Real-time exchange rates</span>
                        </div>
                    </Link>
                    <Link to="/features/bills" className="menu-item">
                        <Layers size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Bill Management</span>
                            <span className="menu-item-description">Schedule & pay bills</span>
                        </div>
                    </Link>
                </div>

                {/* Persona 3: Plus (Growing Business) */}
                <div className="persona-column">
                    <div className="persona-header">PLUS & ADVANCED</div>
                    <Link to="/features/inventory" className="menu-item">
                        <Database size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Inventory Tracking</span>
                            <span className="menu-item-description">Stock levels & orders</span>
                        </div>
                    </Link>
                    <Link to="/features/budgeting" className="menu-item">
                        <BarChart2 size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Project Profitability</span>
                            <span className="menu-item-description">Track project costs</span>
                        </div>
                    </Link>
                </div>

                {/* Persona 4: Advanced (Enterprise) */}
                <div className="persona-column">
                    <div className="persona-header">PLATFORM</div>
                    <Link to="/hybrid-deployment" className="menu-item">
                        <Cloud size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Hybrid Deployment</span>
                            <span className="menu-item-description">Cloud or Local hosting</span>
                        </div>
                    </Link>
                    <Link to="/security" className="menu-item">
                        <Shield size={20} className="menu-item-icon" />
                        <div className="menu-item-content">
                            <span className="menu-item-title">Enterprise Security</span>
                            <span className="menu-item-description">SOC 2 & IFRS Compliant</span>
                        </div>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default MegaMenu;
