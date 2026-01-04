import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const FairValueForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        asset: '',
        measurement_date: new Date().toISOString().split('T')[0],
        fair_value: '0.00',
        valuation_technique: '',
        level: '1',
        notes: ''
    });
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchAssets();
        if (isEditMode) {
            fetchFairValue();
        }
    }, [id]);

    const fetchAssets = async () => {
        try {
            const data = await accountingService.getFixedAssets({ is_active: true });
            setAssets(data.results || data);
        } catch (error) {
            console.error('Error fetching assets:', error);
        }
    };

    const fetchFairValue = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getFairValueMeasurementById(id);
            setFormData({
                asset: data.asset || '',
                measurement_date: data.measurement_date || '',
                fair_value: data.fair_value || '0.00',
                valuation_technique: data.valuation_technique || '',
                level: data.level || '1',
                notes: data.notes || ''
            });
        } catch (error) {
            console.error('Error fetching fair value measurement:', error);
            alert('Failed to load fair value measurement');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.asset) {
            newErrors.asset = 'Asset is required';
        }

        if (!formData.measurement_date) {
            newErrors.measurement_date = 'Measurement date is required';
        }

        if (!formData.fair_value || parseFloat(formData.fair_value) <= 0) {
            newErrors.fair_value = 'Fair value must be greater than 0';
        }

        if (!formData.valuation_technique.trim()) {
            newErrors.valuation_technique = 'Valuation technique is required';
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
                await accountingService.updateFairValueMeasurement(id, formData);
                alert('Fair value measurement updated successfully');
            } else {
                await accountingService.createFairValueMeasurement(formData);
                alert('Fair value measurement created successfully');
            }
            
            navigate('/dashboard/accounting/fair-value-measurements');
        } catch (error) {
            console.error('Error saving fair value measurement:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save fair value measurement');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/fair-value-measurements');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit Fair Value Measurement' : 'New Fair Value Measurement'}
                subtitle="IAS 39 / IFRS 9 Compliance"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">Fair Value Measurement Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="asset">
                                    Asset <span className="required">*</span>
                                </label>
                                <select
                                    id="asset"
                                    name="asset"
                                    value={formData.asset}
                                    onChange={handleChange}
                                    className={errors.asset ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Asset</option>
                                    {assets.map(asset => (
                                        <option key={asset.id} value={asset.id}>
                                            {asset.asset_code} - {asset.asset_name}
                                        </option>
                                    ))}
                                </select>
                                {errors.asset && <span className="error-message">{errors.asset}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="measurement_date">
                                    Measurement Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="measurement_date"
                                    name="measurement_date"
                                    type="date"
                                    value={formData.measurement_date}
                                    onChange={handleChange}
                                    error={errors.measurement_date}
                                    disabled={loading}
                                />
                                {errors.measurement_date && <span className="error-message">{errors.measurement_date}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="fair_value">
                                    Fair Value <span className="required">*</span>
                                </label>
                                <Input
                                    id="fair_value"
                                    name="fair_value"
                                    type="number"
                                    step="0.01"
                                    value={formData.fair_value}
                                    onChange={handleChange}
                                    placeholder="0.00"
                                    error={errors.fair_value}
                                    disabled={loading}
                                />
                                {errors.fair_value && <span className="error-message">{errors.fair_value}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="level">
                                    IFRS 9 Level <span className="required">*</span>
                                </label>
                                <select
                                    id="level"
                                    name="level"
                                    value={formData.level}
                                    onChange={handleChange}
                                    disabled={loading}
                                >
                                    <option value="1">Level 1 - Quoted prices in active markets</option>
                                    <option value="2">Level 2 - Observable inputs other than quoted prices</option>
                                    <option value="3">Level 3 - Unobservable inputs</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="valuation_technique">
                                    Valuation Technique <span className="required">*</span>
                                </label>
                                <Input
                                    id="valuation_technique"
                                    name="valuation_technique"
                                    value={formData.valuation_technique}
                                    onChange={handleChange}
                                    placeholder="e.g., Market approach, Income approach, Cost approach"
                                    error={errors.valuation_technique}
                                    disabled={loading}
                                />
                                {errors.valuation_technique && <span className="error-message">{errors.valuation_technique}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="notes">
                                    Notes
                                </label>
                                <textarea
                                    id="notes"
                                    name="notes"
                                    value={formData.notes}
                                    onChange={handleChange}
                                    placeholder="Additional notes about the fair value measurement..."
                                    rows="3"
                                    disabled={loading}
                                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                                />
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update Fair Value' : 'Create Fair Value')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default FairValueForm;
