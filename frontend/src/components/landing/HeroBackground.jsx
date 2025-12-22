import React from 'react';
import './floating-orbs.css';

const HeroBackground = () => {
    return (
        <div className="orb-container">
            {/* 
                Deep Forensic Visuals:
                Using "Heal and Peace" motion keyframes defined in floating-orbs.css
                3 Orbs with exact Login Page gradients but controlled opacity
            */}
            <div className="orb orb-1"></div>
            <div className="orb orb-2"></div>
            <div className="orb orb-3"></div>

            {/* Optional Grain Overlay for texture if needed */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 400 400\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\' opacity=\'0.05\'/%3E%3C/svg%3E")',
                opacity: 0.4,
                mixBlendMode: 'overlay',
                pointerEvents: 'none'
            }}></div>
        </div>
    );
};

export default HeroBackground;
