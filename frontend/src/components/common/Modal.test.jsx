import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Modal from './Modal';

describe('Modal Component', () => {
    it('should render when isOpen is true', () => {
        render(
            <Modal isOpen={true} onClose={() => { }} title="Test Modal">
                Modal Content
            </Modal>
        );
        expect(screen.getByText('Test Modal')).toBeInTheDocument();
        expect(screen.getByText('Modal Content')).toBeInTheDocument();
    });

    it('should not render when isOpen is false', () => {
        render(
            <Modal isOpen={false} onClose={() => { }} title="Test Modal">
                Modal Content
            </Modal>
        );
        expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
        const handleClose = jest.fn();
        render(
            <Modal isOpen={true} onClose={handleClose} title="Test Modal">
                Content
            </Modal>
        );
        const closeButton = screen.getByRole('button', { name: /close/i });
        fireEvent.click(closeButton);
        expect(handleClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when backdrop is clicked', () => {
        const handleClose = jest.fn();
        render(
            <Modal isOpen={true} onClose={handleClose} title="Test Modal">
                Content
            </Modal>
        );
        const backdrop = screen.getByTestId('modal-backdrop');
        fireEvent.click(backdrop);
        expect(handleClose).toHaveBeenCalledTimes(1);
    });

    it('should not close when modal content is clicked', () => {
        const handleClose = jest.fn();
        render(
            <Modal isOpen={true} onClose={handleClose} title="Test Modal">
                Content
            </Modal>
        );
        const modalContent = screen.getByText('Content');
        fireEvent.click(modalContent);
        expect(handleClose).not.toHaveBeenCalled();
    });

    it('should render footer when provided', () => {
        const footer = <button>Save</button>;
        render(
            <Modal isOpen={true} onClose={() => { }} title="Test Modal" footer={footer}>
                Content
            </Modal>
        );
        expect(screen.getByText('Save')).toBeInTheDocument();
    });

    it('should apply size classes', () => {
        const { container } = render(
            <Modal isOpen={true} onClose={() => { }} title="Test Modal" size="lg">
                Content
            </Modal>
        );
        const modal = container.querySelector('.modal-content');
        expect(modal).toHaveClass('modal-lg');
    });

    it('should call onClose when Escape key is pressed', () => {
        const handleClose = jest.fn();
        render(
            <Modal isOpen={true} onClose={handleClose} title="Test Modal">
                Content
            </Modal>
        );
        fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
        expect(handleClose).toHaveBeenCalledTimes(1);
    });
});
