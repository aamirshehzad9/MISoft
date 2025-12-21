// Pricing data from Master Architecture
export const pricingPlans = [
    {
        id: 'free',
        name: 'Free - Local',
        price: 0,
        period: 'forever',
        description: 'Perfect for solo entrepreneurs and freelancers',
        features: [
            'Full accounting features',
            'Manufacturing ERP',
            'Multi-currency support',
            'Unlimited users',
            'Local deployment',
            'Community support'
        ],
        cta: 'Download Free',
        highlighted: false
    },
    {
        id: 'basic',
        name: 'Cloud Basic',
        price: 29,
        period: 'month',
        description: 'Ideal for small businesses (5-10 users)',
        features: [
            'All free features',
            'Cloud hosting',
            '10 GB storage',
            'Up to 10 users',
            'Daily backups',
            'Email support'
        ],
        cta: 'Start Free Trial',
        highlighted: false
    },
    {
        id: 'premium',
        name: 'Cloud Premium',
        price: 99,
        period: 'month',
        description: 'Best for growing businesses (10-50 users)',
        features: [
            'All basic features',
            '100 GB storage',
            'Unlimited users',
            'Hourly backups',
            'Point-in-time recovery',
            'Priority support + phone'
        ],
        cta: 'Start Free Trial',
        highlighted: true
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: null,
        period: 'custom',
        description: 'For large organizations (50+ users)',
        features: [
            'All premium features',
            'Custom storage',
            'Multi-region deployment',
            'Real-time replication',
            '99.99% uptime SLA',
            'Dedicated account manager'
        ],
        cta: 'Contact Sales',
        highlighted: false
    }
];
