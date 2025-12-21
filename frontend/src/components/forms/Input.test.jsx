import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Input from './Input';

describe('Input Component', () => {
    it('should render input field', () => {
        render(<Input name="test" />);
        const input = screen.getByRole('textbox');
        expect(input).toBeInTheDocument();
    });

    it('should render with label', () => {
        render(<Input label="Test Label" name="test" />);
        expect(screen.getByText('Test Label')).toBeInTheDocument();
    });

    it('should show required indicator when required', () => {
        render(<Input label="Required Field" name="test" required />);
        expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should display placeholder', () => {
        render(<Input placeholder="Enter text" name="test" />);
        const input = screen.getByPlaceholderText('Enter text');
        expect(input).toBeInTheDocument();
    });

    it('should handle value changes', () => {
        const handleChange = jest.fn();
        render(<Input name="test" onChange={handleChange} />);
        const input = screen.getByRole('textbox');
        fireEvent.change(input, { target: { value: 'new value' } });
        expect(handleChange).toHaveBeenCalled();
    });

    it('should display controlled value', () => {
        render(<Input name="test" value="controlled" onChange={() => { }} />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveValue('controlled');
    });

    it('should show error message', () => {
        render(<Input name="test" error="This field is required" />);
        expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should apply error class when error exists', () => {
        render(<Input name="test" error="Error" />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveClass('input-error');
    });

    it('should be disabled when disabled prop is true', () => {
        render(<Input name="test" disabled />);
        const input = screen.getByRole('textbox');
        expect(input).toBeDisabled();
    });

    it('should render as password type', () => {
        render(<Input name="password" type="password" />);
        const input = screen.getByLabelText('password');
        expect(input).toHaveAttribute('type', 'password');
    });

    it('should render as email type', () => {
        render(<Input name="email" type="email" />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveAttribute('type', 'email');
    });

    it('should render as number type', () => {
        render(<Input name="number" type="number" />);
        const input = screen.getByRole('spinbutton');
        expect(input).toHaveAttribute('type', 'number');
    });

    it('should display helper text', () => {
        render(<Input name="test" helperText="This is a hint" />);
        expect(screen.getByText('This is a hint')).toBeInTheDocument();
    });

    it('should render icon when provided', () => {
        const icon = <span data-testid="test-icon">Icon</span>;
        render(<Input name="test" icon={icon} />);
        expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
        render(<Input name="test" className="custom-input" />);
        const wrapper = screen.getByRole('textbox').closest('.input-wrapper');
        expect(wrapper).toHaveClass('custom-input');
    });
});
