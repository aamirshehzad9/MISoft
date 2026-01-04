import React, { useState, useEffect } from 'react';
import { 
    FaPlus, FaSearch, FaEdit, FaTrash, FaUndo, FaListOl 
} from 'react-icons/fa';
import accountingService from '../../services/accounting';
import Modal from '../../components/common/Modal';
import './NumberingSchemes.css';

const NumberingSchemeForm = ({ scheme, onClose, onSave }) => {
    const [formData, setFormData] = useState({
        scheme_name: '',
        document_type: 'invoice',
        prefix: '',
        suffix: '',
        date_format: 'YYYY',
        separator: '-',
        padding: 4,
        reset_frequency: 'yearly',
        is_active: true
    });
    const [preview, setPreview] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (scheme) {
            setFormData({
                scheme_name: scheme.scheme_name,
                document_type: scheme.document_type,
                prefix: scheme.prefix || '',
                suffix: scheme.suffix || '',
                date_format: scheme.date_format,
                separator: scheme.separator,
                padding: scheme.padding,
                reset_frequency: scheme.reset_frequency,
                is_active: scheme.is_active
            });
        }
    }, [scheme]);

    // Update preview when fields change
    useEffect(() => {
        const fetchPreview = async () => {
            try {
                // Client-side preview for responsiveness
                const date = new Date();
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                
                let dateStr = '';
                if (formData.date_format === 'YYYY') dateStr = `${year}`;
                if (formData.date_format === 'YYYYMM') dateStr = `${year}${month}`;
                if (formData.date_format === 'YYYYMMDD') dateStr = `${year}${month}${day}`;
                
                const sep = formData.separator;
                const num = '1'.padStart(formData.padding, '0');
                
                const parts = [formData.prefix, dateStr, num, formData.suffix].filter(Boolean);
                setPreview(parts.join(sep));
            } catch (err) {
                console.error("Preview error", err);
            }
        };
        fetchPreview();
    }, [formData]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onSave(formData);
        } catch (error) {
            console.error('Error saving scheme:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="scheme-form">
            <div className="scheme-form-grid">
                <div className="form-group full-width">
                    <label className="form-label">Scheme Name</label>
                    <input
                        type="text"
                        className="form-input"
                        value={formData.scheme_name}
                        onChange={(e) => setFormData({...formData, scheme_name: e.target.value})}
                        required
                        placeholder="e.g. Sales Invoices 2025"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Document Type</label>
                    <select
                        className="form-select"
                        value={formData.document_type}
                        onChange={(e) => setFormData({...formData, document_type: e.target.value})}
                    >
                        <option value="invoice">Invoice</option>
                        <option value="bill">Bill</option>
                        <option value="payment">Payment</option>
                        <option value="receipt">Receipt</option>
                        <option value="journal">Journal Entry</option>
                        <option value="voucher">Voucher</option>
                        <option value="credit_note">Credit Note</option>
                        <option value="debit_note">Debit Note</option>
                        <option value="purchase_order">Purchase Order</option>
                        <option value="quote">Quote</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Reset Frequency</label>
                    <select
                        className="form-select"
                        value={formData.reset_frequency}
                        onChange={(e) => setFormData({...formData, reset_frequency: e.target.value})}
                    >
                        <option value="never">Never</option>
                        <option value="daily">Daily</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Prefix</label>
                    <input
                        type="text"
                        className="form-input"
                        value={formData.prefix}
                        onChange={(e) => setFormData({...formData, prefix: e.target.value})}
                        placeholder="e.g. INV"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Suffix</label>
                    <input
                        type="text"
                        className="form-input"
                        value={formData.suffix}
                        onChange={(e) => setFormData({...formData, suffix: e.target.value})}
                        placeholder="Optional"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Date Format</label>
                    <select
                        className="form-select"
                        value={formData.date_format}
                        onChange={(e) => setFormData({...formData, date_format: e.target.value})}
                    >
                        <option value="">None</option>
                        <option value="YYYY">YYYY</option>
                        <option value="YYYYMM">YYYYMM</option>
                        <option value="YYYYMMDD">YYYYMMDD</option>
                        <option value="YYMM">YYMM</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Separator</label>
                    <input
                        type="text"
                        className="form-input"
                        value={formData.separator}
                        onChange={(e) => setFormData({...formData, separator: e.target.value})}
                        placeholder="e.g. -"
                        maxLength={1}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Padding (Zeroes)</label>
                    <input
                        type="number"
                        className="form-input"
                        value={formData.padding}
                        onChange={(e) => setFormData({...formData, padding: parseInt(e.target.value)})}
                        min="1"
                        max="10"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Status</label>
                    <select
                        className="form-select"
                        value={formData.is_active}
                        onChange={(e) => setFormData({...formData, is_active: e.target.value === 'true'})}
                    >
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                    </select>
                </div>
            </div>

            <div className="preview-box">
                <span className="preview-label">Live Preview:</span>
                <span className="preview-value">{preview}</span>
            </div>

            <div className="modal-actions" style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : (scheme ? 'Update Scheme' : 'Create Scheme')}
                </button>
            </div>
        </form>
    );
};

const NumberingSchemesList = () => {
    const [schemes, setSchemes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [showModal, setShowModal] = useState(false);
    const [editingScheme, setEditingScheme] = useState(null);
    const [showResetModal, setShowResetModal] = useState(false);
    const [resetTarget, setResetTarget] = useState(null);

    useEffect(() => {
        fetchSchemes();
    }, []);

    const fetchSchemes = async () => {
        try {
            setLoading(true);
            const response = await accountingService.getNumberingSchemes();
            const data = Array.isArray(response) ? response : (response.results || []);
            setSchemes(data);
        } catch (error) {
            console.error('Error fetching schemes:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (data) => {
        try {
            if (editingScheme) {
                await accountingService.updateNumberingScheme(editingScheme.id, data);
            } else {
                await accountingService.createNumberingScheme(data);
            }
            setShowModal(false);
            fetchSchemes();
        } catch (error) {
            console.error('Error saving:', error);
            alert('Failed to save scheme. ' + (error.response?.data?.error || error.message));
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this numbering scheme?')) return;
        try {
            await accountingService.deleteNumberingScheme(id);
            fetchSchemes();
        } catch (error) {
            console.error('Error deleting:', error);
        }
    };

    const handleResetCounter = async () => {
        if (!resetTarget) return;
        try {
            await accountingService.resetCounter(resetTarget.id, { reset_to: 1 });
            setShowResetModal(false);
            setResetTarget(null);
            fetchSchemes();
            alert('Counter reset successfully');
        } catch (error) {
            console.error('Error resetting counter:', error);
        }
    };

    const filteredSchemes = schemes.filter(scheme => {
        const matchesSearch = scheme.scheme_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                              scheme.prefix.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = filterType === 'all' || scheme.document_type === filterType;
        return matchesSearch && matchesType;
    });

    return (
        <div className="numbering-schemes-container">
            <div className="schemes-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ 
                        background: 'var(--primary-color)', 
                        padding: '0.75rem', 
                        borderRadius: '12px',
                        color: 'white',
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center'
                    }}>
                        <FaListOl size={24} />
                    </div>
                    <div>
                        <h1 style={{ margin: 0 }}>Numbering Schemes</h1>
                        <p style={{ margin: '0.25rem 0 0', color: 'var(--text-secondary)' }}>
                            Manage document numbering formats and sequences
                        </p>
                    </div>
                </div>
                <button 
                    className="btn-primary"
                    onClick={() => { setEditingScheme(null); setShowModal(true); }}
                >
                    <FaPlus /> New Scheme
                </button>
            </div>

            <div className="schemes-controls">
                <div className="search-wrapper">
                    <FaSearch className="search-icon" />
                    <input
                        type="text"
                        placeholder="Search schemes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <select 
                    className="filter-select"
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                >
                    <option value="all">All Document Types</option>
                    <option value="invoice">Invoices</option>
                    <option value="payment">Payments</option>
                    <option value="journal">Journals</option>
                    <option value="voucher">Vouchers</option>
                </select>
            </div>

            <div className="schemes-table-container">
                <table className="schemes-table">
                    <thead>
                        <tr>
                            <th>Scheme Name</th>
                            <th>Type</th>
                            <th>Format Preview</th>
                            <th>Next Number</th>
                            <th>Reset Freq</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>Loading...</td></tr>
                        ) : filteredSchemes.length === 0 ? (
                            <tr><td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>No schemes found.</td></tr>
                        ) : (
                            filteredSchemes.map(scheme => (
                                <tr key={scheme.id}>
                                    <td style={{fontWeight: 500}}>{scheme.scheme_name}</td>
                                    <td>
                                        <span style={{textTransform: 'capitalize'}}>
                                            {scheme.document_type.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td>
                                        <span className="preview-pill">
                                            {scheme.preview_number || 'N/A'}
                                        </span>
                                    </td>
                                    <td>{scheme.next_number}</td>
                                    <td style={{textTransform: 'capitalize'}}>{scheme.reset_frequency}</td>
                                    <td>
                                        <span className={`status-badge ${scheme.is_active ? 'status-active' : 'status-inactive'}`}>
                                            {scheme.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="action-buttons">
                                            <button 
                                                className="btn-icon" 
                                                title="Edit"
                                                onClick={() => { setEditingScheme(scheme); setShowModal(true); }}
                                            >
                                                <FaEdit />
                                            </button>
                                            <button 
                                                className="btn-icon reset" 
                                                title="Reset Counter"
                                                onClick={() => { setResetTarget(scheme); setShowResetModal(true); }}
                                            >
                                                <FaUndo />
                                            </button>
                                            <button 
                                                className="btn-icon delete" 
                                                title="Delete"
                                                onClick={() => handleDelete(scheme.id)}
                                            >
                                                <FaTrash />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                title={editingScheme ? 'Edit Numbering Scheme' : 'Create Numbering Scheme'}
            >
                <NumberingSchemeForm 
                    scheme={editingScheme} 
                    onClose={() => setShowModal(false)}
                    onSave={handleSave}
                />
            </Modal>

            <Modal
                isOpen={showResetModal}
                onClose={() => setShowResetModal(false)}
                title="Reset Counter"
            >
                <div>
                    <p>Are you sure you want to reset the counter for <strong>{resetTarget?.scheme_name}</strong>?</p>
                    <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem'}}>
                        The next number allowed will be <strong>1</strong>. This action cannot be undone.
                    </p>
                    <div style={{marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
                        <button className="btn-secondary" onClick={() => setShowResetModal(false)}>Cancel</button>
                        <button className="btn-primary" style={{background: '#f59e0b'}} onClick={handleResetCounter}>Confirm Reset</button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default NumberingSchemesList;
