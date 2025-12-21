import React from 'react';
import './Select.css';

const Select = ({
    label,
    name,
    value,
    onChange,
    options = [],
    placeholder = 'Select...',
    error,
    disabled = false,
    required = false,
    helperText,
    className = '',
    ...props
}) => {
    return (
        <div className={`select-group ${className}`}>
            {label && (
                <label htmlFor={name} className="select-label">
                    {label}
                    {required && <span className="select-required">*</span>}
                </label>
            )}
            <div className={`select-wrapper ${error ? 'select-error' : ''} ${disabled ? 'select-disabled' : ''}`}>
                <select
                    id={name}
                    name={name}
                    value={value}
                    onChange={onChange}
                    disabled={disabled}
                    required={required}
                    className="select-field"
                    {...props}
                >
                    <option value="">{placeholder}</option>
                    {options.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <span className="select-arrow">
                    <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
                        <path d="M1 1L6 6L11 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </span>
            </div>
            {error && <span className="select-error-text">{error}</span>}
            {helperText && !error && <span className="select-helper-text">{helperText}</span>}
        </div>
    );
};

export default Select;
