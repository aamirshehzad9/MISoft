import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const TaxGroupForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        group_name: '',
        description: '',
        is_active: true
    });
    const [taxGroup, setTaxGroup] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (isEditMode) {
            fetchTaxGroup();
        }
    }, [id]);

    const fetchTaxGroup = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getTaxGroupById(id);
            setFormData({
                group_name: data.group_name || '',
                description: data.description || '',
                is_active: data.is_active !== undefined ? data.is_active : true
            });
            setTaxGroup(data);
        } catch (error) {
            console.error('Error fetching tax group:', error);
            alert('Failed to load tax group');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.group_name.trim()) {
            newErrors.group_name = 'Group name is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validate()) {
            return;
        }

        try {
            setLoading(true);
            
            if (isEditMode) {
                await accountingService.updateTaxGroup(id, formData);
                alert('Tax group updated successfully');
            } else {
                await accountingService.createTaxGroup(formData);
                alert('Tax group created successfully');
            }
            
            navigate('/dashboard/accounting/tax-groups');
        } catch (error) {
            console.error('Error saving tax group:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save tax group');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/tax-groups');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Tax Group' : 'New Tax Group'}
                subtitle="Manage compound tax groups"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Tax Group Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="group_name">
                                    Group Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="group_name"
                                    name="group_name"
                                    value={formData.group_name}
                                    onChange={handleChange}
                                    placeholder="e.g., GST + Service Tax"
                                    error={errors.group_name}
                                    disabled={loading}
                                />
                                {errors.group_name && <span className="error-message">{errors.group_name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="description">
                                    Description
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    placeholder="Describe the tax group..."
                                    rows="3"
                                    disabled={loading}
                                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Active</span>
                                </label>
                                <small className="help-text">
                                    Uncheck to deactivate this tax group
                                </small>
                            </div>
                        </div>
                    </div>

                    {isEditMode && taxGroup && taxGroup.items && taxGroup.items.length > 0 && (
                        <div className="form-section">
                            <h3 className="section-title">Tax Items in Group</h3>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ borderBottom: '2px solid #ddd' }}>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>Sequence</th>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>Tax Code</th>
                                        <th style={{ padding: '10px', textAlign: 'left' }}>Tax Name</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Rate</th>
                                        <th style={{ padding: '10px', textAlign: 'center' }}>Compound</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {taxGroup.items.map((item, index) => (
                                        <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                                            <td style={{ padding: '10px' }}>{item.sequence}</td>
                                            <td style={{ padding: '10px' }}>{item.tax_code}</td>
                                            <td style={{ padding: '10px' }}>{item.tax_name}</td>
                                            <td style={{ padding: '10px', textAlign: 'right' }}>{item.tax_rate}%</td>
                                            <td style={{ padding: '10px', textAlign: 'center' }}>
                                                {item.apply_on_previous ? '✓' : '-'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr style={{ borderTop: '2px solid #ddd', fontWeight: 'bold' }}>
                                        <td colSpan="3" style={{ padding: '10px' }}>Total Tax Rate</td>
                                        <td style={{ padding: '10px', textAlign: 'right' }}>
                                            {taxGroup.total_tax_rate ? taxGroup.total_tax_rate.toFixed(2) : '0.00'}%
                                        </td>
                                        <td></td>
                                    </tr>
                                </tfoot>
                            </table>
                            <small className="help-text" style={{ display: 'block', marginTop: '10px' }}>
                                Note: Tax items are managed through Django Admin. This is a read-only view.
                            </small>
                        </div>
                    )}

                    <div className="form-actions">
                        <Button 
                            type="button" 
                            variant="secondary" 
                            onClick={handleCancel}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button 
                            type="submit" 
                            variant="primary"
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : (isEditMode ? 'Update Tax Group' : 'Create Tax Group')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default TaxGroupForm;
