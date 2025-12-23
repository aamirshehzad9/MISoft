import React, { useState, useEffect } from 'react';
import './AIAccountingSlideshow.css';

// Import generated HD frames
import aiEngineFrame from '../../assets/animations/ai_engine_frame.png';
import reconciliationFrame from '../../assets/animations/reconciliation_frame.png';
import financialDashboardFrame from '../../assets/animations/financial_dashboard_frame.png';
import journalEntriesFrame from '../../assets/animations/journal_entries_frame.png';
import aiInsightsFrame from '../../assets/animations/ai_insights_frame.png';

const AIAccountingSlideshow = () => {
    const [currentSlide, setCurrentSlide] = useState(0);
    const [isPaused, setIsPaused] = useState(false);

    const slides = [
        {
            image: aiEngineFrame,
            title: 'AI Engine Initialization',
            description: 'Analyzing 1,247 transactions with autonomous intelligence'
        },
        {
            image: reconciliationFrame,
            title: 'Autonomous Reconciliation',
            description: '98.7% matching accuracy with AI-powered algorithms'
        },
        {
            image: financialDashboardFrame,
            title: 'Real-Time Dashboard',
            description: 'Live financial metrics and performance tracking'
        },
        {
            image: journalEntriesFrame,
            title: 'Automated Journal Entries',
            description: 'AI-generated debit/credit entries with precision'
        },
        {
            image: aiInsightsFrame,
            title: 'AI Insights & Detection',
            description: 'Anomaly detection with 98.5% accuracy'
        }
    ];

    useEffect(() => {
        if (!isPaused) {
            const interval = setInterval(() => {
                setCurrentSlide((prev) => (prev + 1) % slides.length);
            }, 4000); // 4-second intervals

            return () => clearInterval(interval);
        }
    }, [isPaused, slides.length]);

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    return (
        <div
            className="ai-slideshow-container"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
        >
            {/* Slides */}
            <div className="slideshow-wrapper">
                {slides.map((slide, index) => (
                    <div
                        key={index}
                        className={`slide ${index === currentSlide ? 'active' : ''}`}
                    >
                        <img
                            src={slide.image}
                            alt={slide.title}
                            className="slide-image"
                        />
                        <div className="slide-overlay">
                            <h3 className="slide-title">{slide.title}</h3>
                            <p className="slide-description">{slide.description}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Navigation Dots */}
            <div className="slideshow-dots">
                {slides.map((_, index) => (
                    <button
                        key={index}
                        className={`dot ${index === currentSlide ? 'active' : ''}`}
                        onClick={() => goToSlide(index)}
                        aria-label={`Go to slide ${index + 1}`}
                    />
                ))}
            </div>
        </div>
    );
};

export default AIAccountingSlideshow;
