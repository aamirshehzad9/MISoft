import React from 'react';
import './GlassCard.css';

const GlassCard = ({
    children,
    className = '',
    hover = true,
    glow = false,
    ...props
}) => {
    return (
        <div
            className={`glass-card ${hover ? 'glass-card-hover' : ''} ${glow ? 'glass-card-glow' : ''} ${className}`}
            {...props}
        >
            {children}
        </div>
    );
};

export default GlassCard;
