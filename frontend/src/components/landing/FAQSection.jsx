import React, { useState } from 'react';
import { faqData } from '../../data/faq';
import SectionHeading from '../shared/SectionHeading';
import FAQItem from './FAQItem';
import './FAQSection.css';

const FAQSection = () => {
    const [openIndex, setOpenIndex] = useState(null);

    const handleToggle = (index) => {
        setOpenIndex(openIndex === index ? null : index);
    };

    return (
        <section className="faq-section">
            <div className="container">
                <SectionHeading
                    title="Frequently Asked Questions"
                    subtitle="Common questions about data ownership, security, and compliance"
                />

                <div className="faq-list">
                    {faqData.map((faq, index) => (
                        <FAQItem
                            key={index}
                            question={faq.question}
                            answer={faq.answer}
                            isOpen={openIndex === index}
                            onToggle={() => handleToggle(index)}
                        />
                    ))}
                </div>
            </div>
        </section>
    );
};

export default FAQSection;
