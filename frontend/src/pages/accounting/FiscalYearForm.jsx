import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const FiscalYearForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        name: '',
        start_date: '',
        end_date: '',
        is_closed: false
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (isEditMode) {
            fetchFiscalYear();
        }
    }, [id]);

    const fetchFiscalYear = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getFiscalYearById(id);
            setFormData({
                name: data.name || '',
                start_date: data.start_date || '',
                end_date: data.end_date || '',
                is_closed: data.is_closed || false
            });
        } catch (error) {
            console.error('Error fetching fiscal year:', error);
            alert('Failed to load fiscal year');
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
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Fiscal year name is required';
        }

        if (!formData.start_date) {
            newErrors.start_date = 'Start date is required';
        }

        if (!formData.end_date) {
            newErrors.end_date = 'End date is required';
        }

        if (formData.start_date && formData.end_date) {
            if (new Date(formData.start_date) >= new Date(formData.end_date)) {
                newErrors.end_date = 'End date must be after start date';
            }
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
                await accountingService.updateFiscalYear(id, formData);
                alert('Fiscal year updated successfully');
            } else {
                await accountingService.createFiscalYear(formData);
                alert('Fiscal year created successfully');
            }
            
            navigate('/dashboard/accounting/fiscal-years');
        } catch (error) {
            console.error('Error saving fiscal year:', error);
            if (error.response?.data) {
                // Handle backend validation errors
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save fiscal year');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/fiscal-years');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Fiscal Year' : 'New Fiscal Year'}
                subtitle="Manage accounting periods"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Fiscal Year Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="name">
                                    Fiscal Year Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="e.g., FY 2025-2026"
                                    error={errors.name}
                                    disabled={loading}
                                />
                                {errors.name && <span className="error-message">{errors.name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="start_date">
                                    Start Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="start_date"
                                    name="start_date"
                                    type="date"
                                    value={formData.start_date}
                                    onChange={handleChange}
                                    error={errors.start_date}
                                    disabled={loading}
                                />
                                {errors.start_date && <span className="error-message">{errors.start_date}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="end_date">
                                    End Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="end_date"
                                    name="end_date"
                                    type="date"
                                    value={formData.end_date}
                                    onChange={handleChange}
                                    error={errors.end_date}
                                    disabled={loading}
                                />
                                {errors.end_date && <span className="error-message">{errors.end_date}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_closed"
                                        checked={formData.is_closed}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Fiscal Year Closed</span>
                                </label>
                                <small className="help-text">
                                    Check this to close the fiscal year and prevent further transactions
                                </small>
                            </div>
                        </div>
                    </div>

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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Fiscal Year' : 'Create Fiscal Year')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default FiscalYearForm;
