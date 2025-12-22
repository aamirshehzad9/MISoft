import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin, Twitter, Linkedin, Github } from 'lucide-react';
import { footerData } from '../../data/footer';
import logo from '../../assets/logo.png';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-grid">
                    {/* Company Info */}
                    <div className="footer-column">
                        <Link to="/" className="footer-logo-link">
                            <img src={logo} alt="MISoft Logo" className="h-8 w-auto object-contain mb-4" />
                        </Link>
                        <p className="footer-tagline">{footerData.company.tagline}</p>
                        <p className="footer-description">{footerData.company.description}</p>
                    </div>

                    {/* Product Links */}
                    <div className="footer-column">
                        <h4 className="footer-heading">Product</h4>
                        <ul className="footer-links">
                            {footerData.links.product.map((link, index) => (
                                <li key={index}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Company Links */}
                    <div className="footer-column">
                        <h4 className="footer-heading">Company</h4>
                        <ul className="footer-links">
                            {footerData.links.company.map((link, index) => (
                                <li key={index}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Contact Info */}
                    <div className="footer-column">
                        <h4 className="footer-heading">Contact</h4>
                        <div className="contact-info">
                            <div className="contact-item">
                                <MapPin size={16} />
                                <span>{footerData.contact.us.address}</span>
                            </div>
                            <div className="contact-item">
                                <Mail size={16} />
                                <a href={`mailto:${footerData.contact.us.email}`}>
                                    {footerData.contact.us.email}
                                </a>
                            </div>
                            <div className="contact-item">
                                <Phone size={16} />
                                <a href={`tel:${footerData.contact.us.phone}`}>
                                    {footerData.contact.us.phone}
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* Legal Links */}
                    <div className="footer-column">
                        <h4 className="footer-heading">Legal</h4>
                        <ul className="footer-links">
                            {footerData.links.legal.map((link, index) => (
                                <li key={index}>
                                    <Link to={link.path}>{link.label}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                <div className="footer-bottom">
                    <div className="footer-social">
                        <a href={footerData.social.twitter} target="_blank" rel="noopener noreferrer">
                            <Twitter size={20} />
                        </a>
                        <a href={footerData.social.linkedin} target="_blank" rel="noopener noreferrer">
                            <Linkedin size={20} />
                        </a>
                        <a href={footerData.social.github} target="_blank" rel="noopener noreferrer">
                            <Github size={20} />
                        </a>
                    </div>

                    <div className="footer-copyright">
                        <p>© 2025 MISoft. All rights reserved.</p>
                        <p className="powered-by">
                            Powered by <a href="https://gentleomegaai.space" target="_blank" rel="noopener noreferrer">{footerData.poweredBy}</a>
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
