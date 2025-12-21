import React from 'react';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import GlassCard from '../shared/GlassCard';

const PricingCard = ({ plan }) => {
    return (
        <GlassCard
            className={`pricing-card ${plan.highlighted ? 'highlighted' : ''}`}
            hover
        >
            {plan.highlighted && (
                <div className="recommended-badge">Recommended</div>
            )}

            <h3 className="plan-name">{plan.name}</h3>
            <p className="plan-description">{plan.description}</p>

            <div className="plan-price">
                {plan.price !== null ? (
                    <>
                        <span className="price-currency">$</span>
                        <span className="price-amount">{plan.price}</span>
                        <span className="price-period">/{plan.period}</span>
                    </>
                ) : (
                    <span className="price-custom">Custom Pricing</span>
                )}
            </div>

            <ul className="plan-features">
                {plan.features.map((feature, index) => (
                    <li key={index}>
                        <Check size={16} />
                        <span>{feature}</span>
                    </li>
                ))}
            </ul>

            <Link
                to={plan.id === 'free' ? '/download' : plan.id === 'enterprise' ? '/contact' : '/register'}
                className={`plan-cta ${plan.highlighted ? 'btn-primary' : 'btn-secondary'}`}
            >
                {plan.cta}
            </Link>
        </GlassCard>
    );
};

export default PricingCard;
