import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(username, password);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="login-container">
            <div className="login-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
                <div className="gradient-orb orb-3"></div>
            </div>

            <div className="login-card">
                <div className="login-header">
                    <div className="logo-container">
                        <img src="/logo.png" alt="MI Industries" className="logo-image" />
                    </div>
                    <h1>MI Industries</h1>
                    <p>Accounting & Manufacturing Software</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    {error && (
                        <div className="error-message">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor" />
                            </svg>
                            {error}
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <div className="input-wrapper">
                            <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 10C12.7614 10 15 7.76142 15 5C15 2.23858 12.7614 0 10 0C7.23858 0 5 2.23858 5 5C5 7.76142 7.23858 10 10 10Z" fill="currentColor" />
                                <path d="M10 12C5.58172 12 2 15.5817 2 20H18C18 15.5817 14.4183 12 10 12Z" fill="currentColor" />
                            </svg>
                            <input
                                type="text"
                                id="username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter your username"
                                required
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <div className="input-wrapper">
                            <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M15 7H14V5C14 2.24 11.76 0 9 0C6.24 0 4 2.24 4 5V7H3C1.9 7 1 7.9 1 9V18C1 19.1 1.9 20 3 20H15C16.1 20 17 19.1 17 18V9C17 7.9 16.1 7 15 7ZM9 15C7.9 15 7 14.1 7 13C7 11.9 7.9 11 9 11C10.1 11 11 11.9 11 13C11 14.1 10.1 15 9 15ZM12 7H6V5C6 3.34 7.34 2 9 2C10.66 2 12 3.34 12 5V7Z" fill="currentColor" />
                            </svg>
                            <input
                                type="password"
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <button type="submit" className="login-button" disabled={loading}>
                        {loading ? (
                            <div className="spinner"></div>
                        ) : (
                            <>
                                <span>Sign In</span>
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M10 0L8.59 1.41L16.17 9H0V11H16.17L8.59 18.59L10 20L20 10L10 0Z" fill="currentColor" />
                                </svg>
                            </>
                        )}
                    </button>
                </form>

                <div className="login-footer">
                    <p>© 2025 MI Industries. All rights reserved.</p>
                </div>
            </div>
        </div>
    );
};

export default Login;
