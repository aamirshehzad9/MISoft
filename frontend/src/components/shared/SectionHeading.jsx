import React from 'react';
import './SectionHeading.css';

const SectionHeading = ({
    title,
    subtitle,
    align = 'center',
    className = ''
}) => {
    return (
        <div className={`section-heading ${align} ${className}`}>
            <h2 className="section-title">{title}</h2>
            {subtitle && <p className="section-subtitle">{subtitle}</p>}
        </div>
    );
};

export default SectionHeading;
