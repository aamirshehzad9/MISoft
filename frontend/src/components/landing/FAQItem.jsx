import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const FAQItem = ({ question, answer, isOpen, onToggle }) => {
    return (
        <div className={`faq-item ${isOpen ? 'open' : ''}`}>
            <button className="faq-question" onClick={onToggle}>
                <span>{question}</span>
                <ChevronDown size={20} className="chevron" />
            </button>
            <div className="faq-answer">
                <p>{answer}</p>
            </div>
        </div>
    );
};

export default FAQItem;
