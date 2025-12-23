import React from 'react';
import GlassCard from '../shared/GlassCard';

const FeatureCard = ({ title, description, highlights, image }) => {
    return (
        <GlassCard className="feature-card" hover>
            {image && (
                <div className="feature-card-image">
                    <img src={image} alt={title} />
                </div>
            )}
            <h3 className="feature-card-title">{title}</h3>
            <p className="feature-card-description">{description}</p>
            {highlights && (
                <ul className="feature-highlights">
                    {highlights.map((highlight, index) => (
                        <li key={index}>{highlight}</li>
                    ))}
                </ul>
            )}
        </GlassCard>
    );
};

export default FeatureCard;
