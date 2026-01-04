/**
 * QuickAddVariantModal Component
 * Task 1.6.1: Quick-Add Modal Component
 * 
 * Allows users to quickly create product variants from voucher/invoice forms
 * without leaving the current page.
 */

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import './QuickAddVariantModal.css';

const QuickAddVariantModal = ({ isOpen, onClose, onSuccess, product }) => {
  const [formData, setFormData] = useState({
    variant_name: '',
    variant_code: '',
    price_adjustment: '0.00',
    barcode: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const variantNameRef = useRef(null);

  // Focus on first input when modal opens
  useEffect(() => {
    if (isOpen && variantNameRef.current) {
      variantNameRef.current.focus();
    }
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        variant_name: '',
        variant_code: '',
        price_adjustment: '0.00',
        barcode: ''
      });
      setErrors({});
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.variant_name.trim()) {
      newErrors.variant_name = 'Variant name is required';
    }

    if (!formData.variant_code.trim()) {
      newErrors.variant_code = 'Variant code is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const variantData = {
        product: product.id,
        variant_name: formData.variant_name,
        variant_code: formData.variant_code,
        price_adjustment: formData.price_adjustment,
        barcode: formData.barcode || undefined
      };

      await onSuccess(variantData);

      // Reset form after successful submission
      setFormData({
        variant_name: '',
        variant_code: '',
        price_adjustment: '0.00',
        barcode: ''
      });
    } catch (error) {
      console.error('Error creating variant:', error);
      setErrors({
        submit: error.message || 'Failed to create variant'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div 
      className="modal-overlay" 
      onClick={handleOverlayClick}
      data-testid="modal-overlay"
    >
      <div 
        className="modal-container"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="modal-header">
          <h2 id="modal-title">Add Product Variant</h2>
          <p className="modal-subtitle">
            Creating variant for: <strong>{product.name}</strong> ({product.code})
          </p>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="variant_name">
              Variant Name <span className="required">*</span>
            </label>
            <input
              ref={variantNameRef}
              type="text"
              id="variant_name"
              name="variant_name"
              value={formData.variant_name}
              onChange={handleChange}
              placeholder="e.g., Size: Large, Color: Red"
              required
              className={errors.variant_name ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.variant_name && (
              <span className="error-message">{errors.variant_name}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="variant_code">
              Variant Code <span className="required">*</span>
            </label>
            <input
              type="text"
              id="variant_code"
              name="variant_code"
              value={formData.variant_code}
              onChange={handleChange}
              placeholder="e.g., PROD-001-L"
              required
              className={errors.variant_code ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.variant_code && (
              <span className="error-message">{errors.variant_code}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="price_adjustment">
              Price Adjustment
            </label>
            <input
              type="number"
              id="price_adjustment"
              name="price_adjustment"
              value={formData.price_adjustment}
              onChange={handleChange}
              step="0.01"
              placeholder="0.00"
              disabled={isSubmitting}
            />
            <small className="help-text">
              Price difference from base product (can be negative)
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="barcode">
              Barcode <span className="optional">(Optional)</span>
            </label>
            <input
              type="text"
              id="barcode"
              name="barcode"
              value={formData.barcode}
              onChange={handleChange}
              placeholder="Enter barcode"
              disabled={isSubmitting}
            />
          </div>

          {errors.submit && (
            <div className="error-message submit-error">
              {errors.submit}
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Variant'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

QuickAddVariantModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
  product: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    code: PropTypes.string.isRequired
  }).isRequired
};

export default QuickAddVariantModal;
