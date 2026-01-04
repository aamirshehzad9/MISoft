import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const CostCenterForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        code: '',
        name: '',
        description: '',
        is_active: true
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (isEditMode) {
            fetchCostCenter();
        }
    }, [id]);

    const fetchCostCenter = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getCostCenterById(id);
            setFormData({
                code: data.code || '',
                name: data.name || '',
                description: data.description || '',
                is_active: data.is_active !== undefined ? data.is_active : true
            });
        } catch (error) {
            console.error('Error fetching cost center:', error);
            alert('Failed to load cost center');
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

        if (!formData.code.trim()) {
            newErrors.code = 'Cost center code is required';
        }

        if (!formData.name.trim()) {
            newErrors.name = 'Cost center name is required';
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
                await accountingService.updateCostCenter(id, formData);
                alert('Cost center updated successfully');
            } else {
                await accountingService.createCostCenter(formData);
                alert('Cost center created successfully');
            }
            
            navigate('/dashboard/accounting/cost-centers');
        } catch (error) {
            console.error('Error saving cost center:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save cost center');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/cost-centers');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Cost Center' : 'New Cost Center'}
                subtitle="Organizational Cost Tracking"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Cost Center Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="code">
                                    Code <span className="required">*</span>
                                </label>
                                <Input
                                    id="code"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    placeholder="e.g., CC-001, SALES, IT"
                                    error={errors.code}
                                    disabled={loading}
                                />
                                {errors.code && <span className="error-message">{errors.code}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="name">
                                    Name <span className="required">*</span>
                                </label>
                                <Input
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="e.g., Sales Department, IT Department"
                                    error={errors.name}
                                    disabled={loading}
                                />
                                {errors.name && <span className="error-message">{errors.name}</span>}
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
                                    placeholder="Describe the cost center..."
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
                                    Uncheck to deactivate this cost center
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Cost Center' : 'Create Cost Center')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default CostCenterForm;
