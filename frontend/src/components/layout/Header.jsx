import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Header.css';

const Header = ({ onMenuClick }) => {
    const { user, logout } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);

    return (
        <header className="header">
            <div className="header-left">
                <button className="header-menu-btn" onClick={onMenuClick}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                </button>
                <h1 className="header-title">MISoft ERP</h1>
            </div>

            <div className="header-right">
                <div className="header-user" onClick={() => setShowUserMenu(!showUserMenu)}>
                    <div className="header-user-avatar">
                        {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                    </div>
                    <div className="header-user-info">
                        <span className="header-user-name">{user?.first_name || user?.username}</span>
                        <span className="header-user-role">{user?.role}</span>
                    </div>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                </div>

                {showUserMenu && (
                    <div className="header-user-menu">
                        <button className="header-user-menu-item" onClick={logout}>
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M11 3h2v10h-2M7 11l3-3-3-3M10 8H2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;
