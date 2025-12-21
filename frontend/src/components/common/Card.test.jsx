import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Card from './Card';

describe('Card Component', () => {
    it('should render children content', () => {
        render(<Card>Test Content</Card>);
        expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('should render with title', () => {
        render(<Card title="Test Title">Content</Card>);
        expect(screen.getByText('Test Title')).toBeInTheDocument();
    });

    it('should render with subtitle', () => {
        render(<Card title="Title" subtitle="Test Subtitle">Content</Card>);
        expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
        const { container } = render(<Card className="custom-card">Content</Card>);
        expect(container.querySelector('.custom-card')).toBeInTheDocument();
    });

    it('should apply padding classes', () => {
        const { container } = render(<Card padding="lg">Content</Card>);
        const card = container.querySelector('.card');
        expect(card).toHaveClass('card-padding-lg');
    });

    it('should render without title and subtitle', () => {
        render(<Card>Just Content</Card>);
        expect(screen.getByText('Just Content')).toBeInTheDocument();
        expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    });
});
