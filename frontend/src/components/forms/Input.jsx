import React from 'react';
import './Input.css';

const Input = ({
    label,
    name,
    type = 'text',
    value,
    onChange,
    placeholder,
    error,
    disabled = false,
    required = false,
    icon = null,
    helperText,
    className = '',
    ...props
}) => {
    return (
        <div className={`input-group ${className}`}>
            {label && (
                <label htmlFor={name} className="input-label">
                    {label}
                    {required && <span className="input-required">*</span>}
                </label>
            )}
            <div className={`input-wrapper ${error ? 'input-error' : ''} ${disabled ? 'input-disabled' : ''}`}>
                {icon && <span className="input-icon">{icon}</span>}
                <input
                    id={name}
                    name={name}
                    type={type}
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
                    disabled={disabled}
                    required={required}
                    className={`input-field ${icon ? 'input-with-icon' : ''}`}
                    {...props}
                />
            </div>
            {error && <span className="input-error-text">{error}</span>}
            {helperText && !error && <span className="input-helper-text">{helperText}</span>}
        </div>
    );
};

export default Input;
