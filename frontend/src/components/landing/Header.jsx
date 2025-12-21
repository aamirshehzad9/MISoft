import React from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from '../shared/ThemeToggle';
import './Header.css';

const Header = () => {
    return (
        <header className="landing-header">
            <div className="container header-content">
                <Link to="/" className="logo">
                    <span className="logo-text">MI</span>
                    <span className="logo-soft">Soft</span>
                </Link>

                <nav className="nav-menu">
                    <a href="#features" className="nav-link">Features</a>
                    <a href="#pricing" className="nav-link">Pricing</a>
                    <a href="#faq" className="nav-link">FAQ</a>
                </nav>

                <div className="header-actions">
                    <ThemeToggle />
                    <Link to="/login" className="btn btn-secondary">Login</Link>
                    <Link to="/register" className="btn btn-primary">Start Free Trial</Link>
                </div>
            </div>
        </header>
    );
};

export default Header;
