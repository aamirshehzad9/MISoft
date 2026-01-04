/**
 * Integration Tests for ProductVariantQuickAdd
 * Task 1.6.3: Dynamic Dropdown Update
 * 
 * Tests the integration between QuickAddVariantModal and the API,
 * including dropdown updates and auto-selection
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ProductVariantQuickAdd from '../ProductVariantQuickAdd';
import * as productsService from '../../services/productsService';

// Mock the productsService
jest.mock('../../services/productsService');

describe('ProductVariantQuickAdd Integration', () => {
  const mockProduct = {
    id: 1,
    name: 'Test Product',
    code: 'PROD-001'
  };

  const mockOnVariantCreated = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Modal Integration', () => {
    test('should open modal when trigger button is clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      const triggerButton = screen.getByRole('button', { name: /Add Variant/i });
      await user.click(triggerButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    test('should close modal when cancel is clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.click(screen.getByRole('button', { name: /Cancel/i }));

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  describe('API Integration', () => {
    test('should call API when variant is created', async () => {
      const user = userEvent.setup();
      const mockCreatedVariant = {
        id: 10,
        product: 1,
        variant_name: 'Size: Large',
        variant_code: 'PROD-001-L',
        price_adjustment: '10.50',
        barcode: '1234567890',
        is_active: true
      };

      productsService.createVariantQuick = jest.fn().mockResolvedValue(mockCreatedVariant);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      // Open modal
      await user.click(screen.getByRole('button', { name: /Add Variant/i }));

      // Fill form
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.type(screen.getByLabelText(/Price Adjustment/i), '10.50');
      await user.type(screen.getByLabelText(/Barcode/i), '1234567890');

      // Submit
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(productsService.createVariantQuick).toHaveBeenCalledWith({
          product: 1,
          variant_name: 'Size: Large',
          variant_code: 'PROD-001-L',
          price_adjustment: '10.50',
          barcode: '1234567890'
        });
      });
    });

    test('should call onVariantCreated callback after successful creation', async () => {
      const user = userEvent.setup();
      const mockCreatedVariant = {
        id: 10,
        product: 1,
        variant_name: 'Size: Large',
        variant_code: 'PROD-001-L',
        price_adjustment: '10.50',
        is_active: true
      };

      productsService.createVariantQuick = jest.fn().mockResolvedValue(mockCreatedVariant);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(mockOnVariantCreated).toHaveBeenCalledWith(mockCreatedVariant);
      });
    });

    test('should close modal after successful creation', async () => {
      const user = userEvent.setup();
      const mockCreatedVariant = {
        id: 10,
        product: 1,
        variant_name: 'Size: Large',
        variant_code: 'PROD-001-L',
        is_active: true
      };

      productsService.createVariantQuick = jest.fn().mockResolvedValue(mockCreatedVariant);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });
  });

  describe('Success Notification', () => {
    test('should show success notification after variant creation', async () => {
      const user = userEvent.setup();
      const mockCreatedVariant = {
        id: 10,
        product: 1,
        variant_name: 'Size: Large',
        variant_code: 'PROD-001-L',
        is_active: true
      };

      productsService.createVariantQuick = jest.fn().mockResolvedValue(mockCreatedVariant);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(screen.getByText(/Variant created successfully/i)).toBeInTheDocument();
      });
    });

    test('should hide success notification after timeout', async () => {
      jest.useFakeTimers();
      const user = userEvent.setup({ delay: null });
      
      const mockCreatedVariant = {
        id: 10,
        product: 1,
        variant_name: 'Size: Large',
        variant_code: 'PROD-001-L',
        is_active: true
      };

      productsService.createVariantQuick = jest.fn().mockResolvedValue(mockCreatedVariant);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(screen.getByText(/Variant created successfully/i)).toBeInTheDocument();
      });

      // Fast-forward time
      jest.advanceTimersByTime(3000);

      await waitFor(() => {
        expect(screen.queryByText(/Variant created successfully/i)).not.toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Error Handling', () => {
    test('should show error message when API call fails', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Variant with code "PROD-001-L" already exists';

      productsService.createVariantQuick = jest.fn().mockRejectedValue({
        response: {
          data: {
            variant_code: [errorMessage]
          }
        }
      });

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
          onError={mockOnError}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(screen.getByText(new RegExp(errorMessage, 'i'))).toBeInTheDocument();
      });
    });

    test('should call onError callback when creation fails', async () => {
      const user = userEvent.setup();
      const error = new Error('Network error');

      productsService.createVariantQuick = jest.fn().mockRejectedValue(error);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
          onError={mockOnError}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalledWith(error);
      });
    });

    test('should keep modal open when creation fails', async () => {
      const user = userEvent.setup();

      productsService.createVariantQuick = jest.fn().mockRejectedValue(new Error('Failed'));

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      await user.click(screen.getByRole('button', { name: /Add Variant/i }));
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });
    });
  });

  describe('Loading State', () => {
    test('should disable trigger button while creating variant', async () => {
      const user = userEvent.setup();
      let resolveCreate;
      const createPromise = new Promise(resolve => {
        resolveCreate = resolve;
      });

      productsService.createVariantQuick = jest.fn().mockReturnValue(createPromise);

      render(
        <ProductVariantQuickAdd
          product={mockProduct}
          onVariantCreated={mockOnVariantCreated}
        />
      );

      const triggerButton = screen.getByRole('button', { name: /Add Variant/i });
      
      await user.click(triggerButton);
      await user.type(screen.getByLabelText(/Variant Name/i), 'Size: Large');
      await user.type(screen.getByLabelText(/Variant Code/i), 'PROD-001-L');
      await user.click(screen.getByRole('button', { name: /Create Variant/i }));

      // Trigger button should be disabled during creation
      expect(triggerButton).toBeDisabled();

      // Resolve the promise
      resolveCreate({ id: 10, variant_name: 'Size: Large' });

      await waitFor(() => {
        expect(triggerButton).not.toBeDisabled();
      });
    });
  });
});
