import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Table from './Table';

describe('Table Component', () => {
    const columns = [
        { key: 'id', label: 'ID', sortable: true },
        { key: 'name', label: 'Name', sortable: true },
        { key: 'email', label: 'Email', sortable: false },
    ];

    const data = [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com' },
    ];

    it('should render table with columns', () => {
        render(<Table columns={columns} data={data} />);
        expect(screen.getByText('ID')).toBeInTheDocument();
        expect(screen.getByText('Name')).toBeInTheDocument();
        expect(screen.getByText('Email')).toBeInTheDocument();
    });

    it('should render table data', () => {
        render(<Table columns={columns} data={data} />);
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
    });

    it('should show loading state', () => {
        render(<Table columns={columns} data={[]} loading />);
        expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should show empty message when no data', () => {
        render(<Table columns={columns} data={[]} emptyMessage="No records found" />);
        expect(screen.getByText('No records found')).toBeInTheDocument();
    });

    it('should handle row click', () => {
        const handleRowClick = jest.fn();
        render(<Table columns={columns} data={data} onRowClick={handleRowClick} />);
        const firstRow = screen.getByText('John Doe').closest('tr');
        fireEvent.click(firstRow);
        expect(handleRowClick).toHaveBeenCalledWith(data[0]);
    });

    it('should sort data when column header is clicked', () => {
        render(<Table columns={columns} data={data} />);
        const nameHeader = screen.getByText('Name');
        fireEvent.click(nameHeader);
        // After sorting, Bob should come first
        const rows = screen.getAllByRole('row');
        expect(rows[1]).toHaveTextContent('Bob Johnson');
    });

    it('should toggle sort direction on second click', () => {
        render(<Table columns={columns} data={data} />);
        const nameHeader = screen.getByText('Name');

        // First click - ascending
        fireEvent.click(nameHeader);
        let rows = screen.getAllByRole('row');
        expect(rows[1]).toHaveTextContent('Bob Johnson');

        // Second click - descending
        fireEvent.click(nameHeader);
        rows = screen.getAllByRole('row');
        expect(rows[1]).toHaveTextContent('John Doe');
    });

    it('should not sort non-sortable columns', () => {
        render(<Table columns={columns} data={data} />);
        const emailHeader = screen.getByText('Email');
        fireEvent.click(emailHeader);
        // Data should remain in original order
        const rows = screen.getAllByRole('row');
        expect(rows[1]).toHaveTextContent('John Doe');
    });

    it('should render custom cell content', () => {
        const customColumns = [
            {
                key: 'name',
                label: 'Name',
                render: (value, row) => <strong>{value.toUpperCase()}</strong>
            }
        ];
        render(<Table columns={customColumns} data={data} />);
        expect(screen.getByText('JOHN DOE')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
        const { container } = render(<Table columns={columns} data={data} className="custom-table" />);
        expect(container.querySelector('.custom-table')).toBeInTheDocument();
    });
});
