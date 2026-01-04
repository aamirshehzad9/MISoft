/**
 * ProductVariantQuickAdd Integration Component
 * Task 1.6.3: Dynamic Dropdown Update
 * 
 * Integrates QuickAddVariantModal with API calls and handles:
 * - Variant creation via AJAX
 * - Success notifications
 * - Error handling
 * - Callback to parent component for dropdown updates
 */

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import QuickAddVariantModal from './QuickAddVariantModal';
import { createVariantQuick } from '../services/productsService';
import './ProductVariantQuickAdd.css';

const ProductVariantQuickAdd = ({ 
  product, 
  onVariantCreated, 
  onError,
  buttonText = 'Add Variant',
  buttonClassName = 'btn btn-sm btn-outline-primary'
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSuccess = async (variantData) => {
    setIsCreating(true);

    try {
      // Call API to create variant
      const createdVariant = await createVariantQuick(variantData);

      // Close modal
      setIsModalOpen(false);

      // Show success notification
      setSuccessMessage(`Variant "${createdVariant.variant_name}" created successfully!`);
      setShowSuccess(true);

      // Hide notification after 3 seconds
      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);

      // Notify parent component to update dropdown
      if (onVariantCreated) {
        onVariantCreated(createdVariant);
      }
    } catch (error) {
      // Handle error
      console.error('Failed to create variant:', error);
      
      // Notify parent component of error
      if (onError) {
        onError(error);
      }

      // Re-throw error so modal can display it
      throw error;
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="product-variant-quick-add">
      <button
        type="button"
        onClick={handleOpenModal}
        className={buttonClassName}
        disabled={isCreating}
      >
        {buttonText}
      </button>

      <QuickAddVariantModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSuccess={handleSuccess}
        product={product}
      />

      {showSuccess && (
        <div className="success-notification" role="alert">
          <span className="success-icon">✓</span>
          {successMessage}
        </div>
      )}
    </div>
  );
};

ProductVariantQuickAdd.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    code: PropTypes.string.isRequired
  }).isRequired,
  onVariantCreated: PropTypes.func.isRequired,
  onError: PropTypes.func,
  buttonText: PropTypes.string,
  buttonClassName: PropTypes.string
};

export default ProductVariantQuickAdd;
