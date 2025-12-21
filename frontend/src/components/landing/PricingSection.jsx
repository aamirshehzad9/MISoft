import React from 'react';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { pricingPlans } from '../../utils/pricing';
import GlassCard from '../shared/GlassCard';
import SectionHeading from '../shared/SectionHeading';
import PricingCard from './PricingCard';
import './PricingSection.css';

const PricingSection = () => {
    return (
        <section className="pricing-section">
            <div className="container">
                <SectionHeading
                    title="Transparent Pricing"
                    subtitle="Choose the plan that fits your business. All plans include full accounting features."
                />

                <div className="pricing-grid">
                    {pricingPlans.map((plan) => (
                        <PricingCard key={plan.id} plan={plan} />
                    ))}
                </div>

                <div className="pricing-note">
                    <p>
                        <strong>14-Day Free Trial:</strong> Try any cloud plan risk-free.
                        No credit card required. Cancel anytime.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default PricingSection;
