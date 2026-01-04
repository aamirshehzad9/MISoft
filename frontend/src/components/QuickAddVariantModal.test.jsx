/**
 * Unit Tests for QuickAddVariantModal Component
 * Task 1.6.1: Quick-Add Modal Component
 * TDD Cycle - Step 1: Write Failing Tests First
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import QuickAddVariantModal from '../QuickAddVariantModal';

describe('QuickAddVariantModal', () => {
  const mockProduct = {
    id: 1,
    name: 'Test Product',
    code: 'PROD-001'
  };

  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('should render modal when isOpen is true', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/Add Product Variant/i)).toBeInTheDocument();
    });

    test('should not render modal when isOpen is false', () => {
      render(
        <QuickAddVariantModal
          isOpen={false}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    test('should display product name in modal header', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      expect(screen.getByText(/Test Product/i)).toBeInTheDocument();
    });

    test('should render all required form fields', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      expect(screen.getByLabelText(/Variant Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Variant Code/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Price Adjustment/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Barcode/i)).toBeInTheDocument();
    });

    test('should mark variant name as required', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantNameInput = screen.getByLabelText(/Variant Name/i);
      expect(variantNameInput).toBeRequired();
    });

    test('should mark variant code as required', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantCodeInput = screen.getByLabelText(/Variant Code/i);
      expect(variantCodeInput).toBeRequired();
    });

    test('should mark barcode as optional', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const barcodeInput = screen.getByLabelText(/Barcode/i);
      expect(barcodeInput).not.toBeRequired();
    });
  });

  describe('Form Interaction', () => {
    test('should allow typing in variant name field', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantNameInput = screen.getByLabelText(/Variant Name/i);
      await user.type(variantNameInput, 'Size: Large');

      expect(variantNameInput).toHaveValue('Size: Large');
    });

    test('should allow typing in variant code field', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantCodeInput = screen.getByLabelText(/Variant Code/i);
      await user.type(variantCodeInput, 'PROD-001-L');

      expect(variantCodeInput).toHaveValue('PROD-001-L');
    });

    test('should allow typing in price adjustment field', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const priceInput = screen.getByLabelText(/Price Adjustment/i);
      await user.type(priceInput, '10.50');

      expect(priceInput).toHaveValue(10.5);
    });

    test('should allow negative price adjustment', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const priceInput = screen.getByLabelText(/Price Adjustment/i);
      await user.type(priceInput, '-5.00');

      expect(priceInput).toHaveValue(-5);
    });
  });

  describe('Form Validation', () => {
    test('should show error when variant name is empty on submit', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Variant name is required/i)).toBeInTheDocument();
      });
    });

    test('should show error when variant code is empty on submit', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantNameInput = screen.getByLabelText(/Variant Name/i);
      await user.type(variantNameInput, 'Size: Large');

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Variant code is required/i)).toBeInTheDocument();
      });
    });

    test('should not submit form when required fields are empty', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      expect(mockOnSuccess).not.toHaveBeenCalled();
    });
  });

  describe('Modal Actions', () => {
    test('should call onClose when cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('should call onClose when clicking outside modal (overlay)', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const overlay = screen.getByTestId('modal-overlay');
      await user.click(overlay);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('should call onSuccess with form data when form is valid', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.type(screen.getByLabelText(/Price Adjustment/i), '10.50');
      await user.type(screen.getByLabelText(/Barcode/i), '1234567890');

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith({
          product: mockProduct.id,
          variant_name: 'Size: Large',
          variant_code: 'PROD-001-L',
          price_adjustment: '10.50',
          barcode: '1234567890'
        });
      });
    });

    test('should reset form after successful submission', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/Variant Name/i)).toHaveValue('');
        expect(screen.getByLabelText(/Variant Code/i)).toHaveValue('');
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-labelledby');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
    });

    test('should focus on first input when modal opens', () => {
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      const variantNameInput = screen.getByLabelText(/Variant Name/i);
      expect(variantNameInput).toHaveFocus();
    });

    test('should close modal on Escape key press', async () => {
      const user = userEvent.setup();
      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
          product={mockProduct}
        />
      );

      await user.keyboard('{Escape}');

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Loading State', () => {
    test('should show loading indicator when submitting', async () => {
      const user = userEvent.setup();
      const slowOnSuccess = jest.fn(() => new Promise(resolve => setTimeout(resolve, 1000)));

      render(
        <QuickAddVariantModal
          isOpen={true}
          onClose={mockOnClose}
          onSuccess={slowOnSuccess}
          product={mockProduct}
        />
      );

      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');

      const submitButton = screen.getByRole('button', { name: /Create Variant/i });
      await user.click(submitButton);

      expect(screen.getByText(/Creating.../i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });
});
