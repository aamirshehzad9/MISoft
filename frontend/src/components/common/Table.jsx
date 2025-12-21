import React, { useState } from 'react';
import './Table.css';

const Table = ({
    columns = [],
    data = [],
    loading = false,
    emptyMessage = 'No data available',
    onRowClick,
    className = '',
}) => {
    const [sortColumn, setSortColumn] = useState(null);
    const [sortDirection, setSortDirection] = useState('asc');

    const handleSort = (column) => {
        if (!column.sortable) return;

        if (sortColumn === column.key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortColumn(column.key);
            setSortDirection('asc');
        }
    };

    const sortedData = React.useMemo(() => {
        if (!sortColumn) return data;

        return [...data].sort((a, b) => {
            const aVal = a[sortColumn];
            const bVal = b[sortColumn];

            if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }, [data, sortColumn, sortDirection]);

    if (loading) {
        return (
            <div className="table-loading">
                <div className="table-spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (data.length === 0) {
        return (
            <div className="table-empty">
                <p>{emptyMessage}</p>
            </div>
        );
    }

    return (
        <div className={`table-container ${className}`}>
            <table className="table">
                <thead className="table-header">
                    <tr>
                        {columns.map((column) => (
                            <th
                                key={column.key}
                                className={`table-header-cell ${column.sortable ? 'sortable' : ''}`}
                                onClick={() => handleSort(column)}
                                style={{ width: column.width }}
                            >
                                <div className="table-header-content">
                                    {column.label}
                                    {column.sortable && sortColumn === column.key && (
                                        <span className="sort-icon">
                                            {sortDirection === 'asc' ? '↑' : '↓'}
                                        </span>
                                    )}
                                </div>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="table-body">
                    {sortedData.map((row, rowIndex) => (
                        <tr
                            key={rowIndex}
                            className={`table-row ${onRowClick ? 'clickable' : ''}`}
                            onClick={() => onRowClick && onRowClick(row)}
                        >
                            {columns.map((column) => (
                                <td key={column.key} className="table-cell">
                                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Table;
