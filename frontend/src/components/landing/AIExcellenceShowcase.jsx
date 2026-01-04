import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import './AIExcellenceShowcase.css';

const AIExcellenceShowcase = () => {
    const [currentSlide, setCurrentSlide] = useState(0);
    const [isPaused, setIsPaused] = useState(false);

    const slides = [
        {
            image: '/showcase/slide1.png',
            title: 'AI Enhancing Financial Accuracy',
            description: 'Witness how artificial intelligence amplifies human potential in financial analysis and decision-making.'
        },
        {
            image: '/showcase/slide2.png',
            title: 'Intelligent Automation',
            description: 'AI automating complex accounting workflows while maintaining precision and compliance.'
        },
        {
            image: '/showcase/slide3.png',
            title: 'Instant Reconciliation',
            description: 'AI matching thousands of transactions in seconds with 99.9% accuracy.'
        },
        {
            image: '/showcase/slide4.png',
            title: 'Regulatory Excellence',
            description: 'AI ensuring perfect IFRS compliance across all financial operations.'
        },
        {
            image: '/showcase/slide5.png',
            title: 'Global Financial Intelligence',
            description: 'AI processing 150+ currencies seamlessly with real-time exchange rates.'
        }
    ];

    const statistics = [
        { emoji: '💸', value: '10,000+', label: 'Successful Transactions' },
        { emoji: '🏢', value: '500+', label: 'Enterprise Clients' },
        { emoji: '📊', value: '1M+', label: 'Records Processed' },
        { emoji: '🌟', value: '4.9/5', label: 'Average Rating' }
    ];

    // Auto-carousel with 4-second interval
    useEffect(() => {
        if (!isPaused) {
            const interval = setInterval(() => {
                setCurrentSlide((prev) => (prev + 1) % slides.length);
            }, 4000); // 4 seconds

            return () => clearInterval(interval);
        }
    }, [isPaused, slides.length]);

    const nextSlide = () => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
    };

    const prevSlide = () => {
        setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
    };

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    return (
        <section className="ai-excellence-section">
            <div className="container">
                <div className="section-header">
                    <h2 className="section-title">
                        AI-Powered <span className="highlight-cyan">Financial Excellence</span>
                    </h2>
                    <p className="section-subtitle">
                        Explore our interactive gallery showcasing the harmonious relationship between
                        artificial intelligence and financial precision.
                    </p>
                </div>

                <div 
                    className="carousel-container"
                    onMouseEnter={() => setIsPaused(true)}
                    onMouseLeave={() => setIsPaused(false)}
                >
                    <div className="main-slide">
                        <img
                            src={slides[currentSlide].image}
                            alt={slides[currentSlide].title}
                            className="slide-image"
                        />
                        <div className="slide-content">
                            <h3 className="slide-title">{slides[currentSlide].title}</h3>
                            <p className="slide-description">{slides[currentSlide].description}</p>
                        </div>

                        <button className="carousel-btn prev-btn" onClick={prevSlide}>
                            <ChevronLeft size={24} />
                        </button>
                        <button className="carousel-btn next-btn" onClick={nextSlide}>
                            <ChevronRight size={24} />
                        </button>

                        <div className="slide-indicators">
                            {slides.map((_, index) => (
                                <button
                                    key={index}
                                    className={`indicator ${index === currentSlide ? 'active' : ''}`}
                                    onClick={() => goToSlide(index)}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="thumbnail-strip">
                        {slides.map((slide, index) => (
                            <button
                                key={index}
                                className={`thumbnail ${index === currentSlide ? 'active' : ''}`}
                                onClick={() => goToSlide(index)}
                            >
                                <img src={slide.image} alt={`Slide ${index + 1}`} />
                            </button>
                        ))}
                    </div>
                </div>

                <div className="statistics-row">
                    {statistics.map((stat, index) => (
                        <div key={index} className="stat-card">
                            <div className="stat-emoji">{stat.emoji}</div>
                            <div className="stat-value">{stat.value}</div>
                            <div className="stat-label">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default AIExcellenceShowcase;
