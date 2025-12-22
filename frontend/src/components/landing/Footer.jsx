import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin, Twitter, Linkedin, Github } from 'lucide-react';
import { footerData } from '../../data/footer';
import logo from '../../assets/logo.png';
import './Footer.css';

const Footer = () => {
    // Footer Data usually imported, but for safety in this hotfix, I'll access it safely or mock it if needed.
    // Assuming footerData is imported correctly.

    return (
        <footer className="w-full bg-[#050505] text-white pt-20 pb-10 border-t border-gray-800">
            <div className="container mx-auto px-4 md:px-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12 mb-16">
                    {/* Brand Column */}
                    <div className="lg:col-span-2">
                        <Link to="/" className="flex items-center gap-3 mb-6 text-decoration-none">
                            <img src={logo} alt="MISoft" className="h-10 w-auto object-contain bg-white rounded p-1" />
                            <span className="text-2xl font-bold tracking-tight text-white">MISoft</span>
                        </Link>
                        <p className="text-gray-400 text-sm leading-relaxed mb-6 max-w-sm">
                            Enterprise AI accounting & finance platform for modern business.
                            IFRS-compliant, hybrid deployment, and bank-level security.
                        </p>

                        {/* Socials - Using footerData if available, safely */}
                        <div className="flex items-center gap-4">
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                                <Twitter size={18} />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                                <Linkedin size={18} />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:bg-[#15D46C] hover:text-white transition-all">
                                <Github size={18} />
                            </a>
                        </div>
                    </div>

                    {/* Dynamic Links Columns from footerData */}
                    {footerData && footerData.links && (
                        <>
                            <div className="lg:col-span-1">
                                <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-xs">Product</h4>
                                <ul className="flex flex-col gap-3">
                                    {footerData.links.product.map((link, idx) => (
                                        <li key={idx}>
                                            <Link to={link.path} className="text-gray-400 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                                {link.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="lg:col-span-1">
                                <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-xs">Company</h4>
                                <ul className="flex flex-col gap-3">
                                    {footerData.links.company.map((link, idx) => (
                                        <li key={idx}>
                                            <Link to={link.path} className="text-gray-400 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                                {link.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="lg:col-span-1">
                                <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-xs">Support</h4>
                                <ul className="flex flex-col gap-3">
                                    {footerData.links.legal.map((link, idx) => (
                                        <li key={idx}>
                                            <Link to={link.path} className="text-gray-400 hover:text-[#15D46C] text-sm transition-colors text-decoration-none">
                                                {link.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </>
                    )}
                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-gray-500 text-sm">© 2025 MISoft. All rights reserved.</p>
                    <p className="text-gray-500 text-sm">
                        Powered by <a href="https://gentleomegaai.space" className="text-gray-400 hover:text-white">Gentle Omega Holding</a>
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
