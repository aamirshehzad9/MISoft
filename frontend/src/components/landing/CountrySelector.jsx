import React, { useState } from 'react';
import { Search, Globe, X } from 'lucide-react';
import '../shared/GlassCard.css';
import './country-selector.css';

const CountrySelector = ({ onClose }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const regions = [
        { name: 'Pakistan', flag: '🇵🇰', lang: 'English' },
        { name: 'United States', flag: '🇺🇸', lang: 'English' },
        { name: 'United Kingdom', flag: '🇬🇧', lang: 'English' },
        { name: 'UAE', flag: '🇦🇪', lang: 'English/Arabic' },
        { name: 'Saudi Arabia', flag: '🇸🇦', lang: 'Arabic' },
    ];

    const filteredRegions = regions.filter(r =>
        r.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="country-modal-overlay">
            <div className="glass-card country-modal">
                <div className="modal-header">
                    <h3>Select your region</h3>
                    <button onClick={onClose} className="close-btn">
                        <X size={24} />
                    </button>
                </div>

                <div className="search-container">
                    <Search size={20} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Find a country or region"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="region-search-input"
                    />
                </div>

                <div className="regions-grid">
                    {filteredRegions.map((region, idx) => (
                        <button key={idx} className="region-btn">
                            <span className="region-flag">{region.flag}</span>
                            <div className="region-info">
                                <span className="region-name">{region.name}</span>
                                <span className="region-lang">{region.lang}</span>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default CountrySelector;
