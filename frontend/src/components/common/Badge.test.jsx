import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Badge from './Badge';

describe('Badge Component', () => {
    it('should render with children text', () => {
        render(<Badge>Active</Badge>);
        expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('should apply default variant class', () => {
        render(<Badge variant="default">Default</Badge>);
        const badge = screen.getByText('Default');
        expect(badge).toHaveClass('badge-default');
    });

    it('should apply primary variant class', () => {
        render(<Badge variant="primary">Primary</Badge>);
        const badge = screen.getByText('Primary');
        expect(badge).toHaveClass('badge-primary');
    });

    it('should apply success variant class', () => {
        render(<Badge variant="success">Success</Badge>);
        const badge = screen.getByText('Success');
        expect(badge).toHaveClass('badge-success');
    });

    it('should apply warning variant class', () => {
        render(<Badge variant="warning">Warning</Badge>);
        const badge = screen.getByText('Warning');
        expect(badge).toHaveClass('badge-warning');
    });

    it('should apply danger variant class', () => {
        render(<Badge variant="danger">Danger</Badge>);
        const badge = screen.getByText('Danger');
        expect(badge).toHaveClass('badge-danger');
    });

    it('should apply info variant class', () => {
        render(<Badge variant="info">Info</Badge>);
        const badge = screen.getByText('Info');
        expect(badge).toHaveClass('badge-info');
    });

    it('should apply small size class', () => {
        render(<Badge size="sm">Small</Badge>);
        const badge = screen.getByText('Small');
        expect(badge).toHaveClass('badge-sm');
    });

    it('should apply large size class', () => {
        render(<Badge size="lg">Large</Badge>);
        const badge = screen.getByText('Large');
        expect(badge).toHaveClass('badge-lg');
    });

    it('should apply custom className', () => {
        render(<Badge className="custom-badge">Custom</Badge>);
        const badge = screen.getByText('Custom');
        expect(badge).toHaveClass('custom-badge');
    });
});
