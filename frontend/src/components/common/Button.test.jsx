import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from './Button';

describe('Button Component', () => {
    it('should render with children text', () => {
        render(<Button>Click Me</Button>);
        expect(screen.getByText('Click Me')).toBeInTheDocument();
    });

    it('should apply primary variant class', () => {
        render(<Button variant="primary">Primary</Button>);
        const button = screen.getByText('Primary');
        expect(button).toHaveClass('btn-primary');
    });

    it('should apply secondary variant class', () => {
        render(<Button variant="secondary">Secondary</Button>);
        const button = screen.getByText('Secondary');
        expect(button).toHaveClass('btn-secondary');
    });

    it('should apply success variant class', () => {
        render(<Button variant="success">Success</Button>);
        const button = screen.getByText('Success');
        expect(button).toHaveClass('btn-success');
    });

    it('should apply danger variant class', () => {
        render(<Button variant="danger">Danger</Button>);
        const button = screen.getByText('Danger');
        expect(button).toHaveClass('btn-danger');
    });

    it('should apply small size class', () => {
        render(<Button size="sm">Small</Button>);
        const button = screen.getByText('Small');
        expect(button).toHaveClass('btn-sm');
    });

    it('should apply large size class', () => {
        render(<Button size="lg">Large</Button>);
        const button = screen.getByText('Large');
        expect(button).toHaveClass('btn-lg');
    });

    it('should handle click events', () => {
        const handleClick = jest.fn();
        render(<Button onClick={handleClick}>Click Me</Button>);
        const button = screen.getByText('Click Me');
        fireEvent.click(button);
        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should be disabled when disabled prop is true', () => {
        render(<Button disabled>Disabled</Button>);
        const button = screen.getByText('Disabled');
        expect(button).toBeDisabled();
    });

    it('should not trigger click when disabled', () => {
        const handleClick = jest.fn();
        render(<Button disabled onClick={handleClick}>Disabled</Button>);
        const button = screen.getByText('Disabled');
        fireEvent.click(button);
        expect(handleClick).not.toHaveBeenCalled();
    });

    it('should show loading state', () => {
        render(<Button loading>Loading</Button>);
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
    });

    it('should render icon when provided', () => {
        const icon = <span data-testid="test-icon">Icon</span>;
        render(<Button icon={icon}>With Icon</Button>);
        expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
        render(<Button className="custom-class">Custom</Button>);
        const button = screen.getByText('Custom');
        expect(button).toHaveClass('custom-class');
    });

    it('should render as submit type', () => {
        render(<Button type="submit">Submit</Button>);
        const button = screen.getByText('Submit');
        expect(button).toHaveAttribute('type', 'submit');
    });

    it('should render as button type by default', () => {
        render(<Button>Default</Button>);
        const button = screen.getByText('Default');
        expect(button).toHaveAttribute('type', 'button');
    });
});
