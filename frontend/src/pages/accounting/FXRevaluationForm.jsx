import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './AccountForm.css';

const FXRevaluationForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        revaluation_id: '',
        entity: '',
        revaluation_date: new Date().toISOString().split('T')[0],
        functional_currency: '',
        accounts_revalued: 0,
        total_gain: '0.00',
        total_loss: '0.00',
        net_fx_gain_loss: '0.00',
        status: 'initiated',
        execution_method: 'manual',
        auto_posted: false,
        reversal_created: false,
        notes: ''
    });
    const [entities, setEntities] = useState([]);
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        fetchEntities();
        fetchCurrencies();
        if (isEditMode) {
            fetchFXRevaluation();
        }
    }, [id]);

    const fetchEntities = async () => {
        try {
            const data = await accountingService.getEntities({ is_active: true });
            setEntities(data.results || data);
        } catch (error) {
            console.error('Error fetching entities:', error);
        }
    };

    const fetchCurrencies = async () => {
        try {
            const data = await accountingService.getCurrencies({ is_active: true });
            setCurrencies(data.results || data);
        } catch (error) {
            console.error('Error fetching currencies:', error);
        }
    };

    const fetchFXRevaluation = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getFXRevaluationLogById(id);
            setFormData({
                revaluation_id: data.revaluation_id || '',
                entity: data.entity || '',
                revaluation_date: data.revaluation_date || '',
                functional_currency: data.functional_currency || '',
                accounts_revalued: data.accounts_revalued || 0,
                total_gain: data.total_gain || '0.00',
                total_loss: data.total_loss || '0.00',
                net_fx_gain_loss: data.net_fx_gain_loss || '0.00',
                status: data.status || 'initiated',
                execution_method: data.execution_method || 'manual',
                auto_posted: data.auto_posted || false,
                reversal_created: data.reversal_created || false,
                notes: data.notes || ''
            });
        } catch (error) {
            console.error('Error fetching FX revaluation log:', error);
            alert('Failed to load FX revaluation log');
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

        if (!formData.revaluation_id.trim()) {
            newErrors.revaluation_id = 'Revaluation ID is required';
        }

        if (!formData.entity) {
            newErrors.entity = 'Entity is required';
        }

        if (!formData.revaluation_date) {
            newErrors.revaluation_date = 'Revaluation date is required';
        }

        if (!formData.functional_currency) {
            newErrors.functional_currency = 'Functional currency is required';
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
                await accountingService.updateFXRevaluationLog(id, formData);
                alert('FX revaluation log updated successfully');
            } else {
                await accountingService.createFXRevaluationLog(formData);
                alert('FX revaluation log created successfully');
            }
            
            navigate('/dashboard/accounting/fx-revaluation-logs');
        } catch (error) {
            console.error('Error saving FX revaluation log:', error);
            if (error.response?.data) {
                const backendErrors = {};
                Object.keys(error.response.data).forEach(key => {
                    backendErrors[key] = Array.isArray(error.response.data[key]) 
                        ? error.response.data[key][0] 
                        : error.response.data[key];
                });
                setErrors(backendErrors);
            } else {
                alert('Failed to save FX revaluation log');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboard/accounting/fx-revaluation-logs');
    };

    return (
        <div className="account-form-page">
            <Card 
                title={isEditMode ? 'Edit FX Revaluation Log' : 'New FX Revaluation Log'}
                subtitle="IAS 21 - Foreign Exchange Revaluation"
            >
                <form onSubmit={handleSubmit} className="account-form">
                    <div className="form-section">
                        <h3 className="section-title">FX Revaluation Information</h3>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="revaluation_id">
                                    Revaluation ID <span className="required">*</span>
                                </label>
                                <Input
                                    id="revaluation_id"
                                    name="revaluation_id"
                                    value={formData.revaluation_id}
                                    onChange={handleChange}
                                    placeholder="e.g., FX-2024-12-001"
                                    error={errors.revaluation_id}
                                    disabled={loading}
                                />
                                {errors.revaluation_id && <span className="error-message">{errors.revaluation_id}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="revaluation_date">
                                    Revaluation Date <span className="required">*</span>
                                </label>
                                <Input
                                    id="revaluation_date"
                                    name="revaluation_date"
                                    type="date"
                                    value={formData.revaluation_date}
                                    onChange={handleChange}
                                    error={errors.revaluation_date}
                                    disabled={loading}
                                />
                                {errors.revaluation_date && <span className="error-message">{errors.revaluation_date}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="entity">
                                    Entity <span className="required">*</span>
                                </label>
                                <select
                                    id="entity"
                                    name="entity"
                                    value={formData.entity}
                                    onChange={handleChange}
                                    className={errors.entity ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Entity</option>
                                    {entities.map(entity => (
                                        <option key={entity.id} value={entity.id}>
                                            {entity.code} - {entity.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.entity && <span className="error-message">{errors.entity}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="functional_currency">
                                    Functional Currency <span className="required">*</span>
                                </label>
                                <select
                                    id="functional_currency"
                                    name="functional_currency"
                                    value={formData.functional_currency}
                                    onChange={handleChange}
                                    className={errors.functional_currency ? 'error' : ''}
                                    disabled={loading}
                                >
                                    <option value="">Select Currency</option>
                                    {currencies.map(curr => (
                                        <option key={curr.id} value={curr.id}>
                                            {curr.currency_code} - {curr.currency_name}
                                        </option>
                                    ))}
                                </select>
                                {errors.functional_currency && <span className="error-message">{errors.functional_currency}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="accounts_revalued">
                                    Accounts Revalued
                                </label>
                                <Input
                                    id="accounts_revalued"
                                    name="accounts_revalued"
                                    type="number"
                                    value={formData.accounts_revalued}
                                    onChange={handleChange}
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="status">
                                    Status
                                </label>
                                <select
                                    id="status"
                                    name="status"
                                    value={formData.status}
                                    onChange={handleChange}
                                    disabled={loading}
                                >
                                    <option value="initiated">Initiated</option>
                                    <option value="calculated">Calculated</option>
                                    <option value="posted">Posted</option>
                                    <option value="reversed">Reversed</option>
                                    <option value="error">Error</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="total_gain">
                                    Total Gain
                                </label>
                                <Input
                                    id="total_gain"
                                    name="total_gain"
                                    type="number"
                                    step="0.01"
                                    value={formData.total_gain}
                                    onChange={handleChange}
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="total_loss">
                                    Total Loss
                                </label>
                                <Input
                                    id="total_loss"
                                    name="total_loss"
                                    type="number"
                                    step="0.01"
                                    value={formData.total_loss}
                                    onChange={handleChange}
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="net_fx_gain_loss">
                                    Net FX Gain/(Loss)
                                </label>
                                <Input
                                    id="net_fx_gain_loss"
                                    name="net_fx_gain_loss"
                                    type="number"
                                    step="0.01"
                                    value={formData.net_fx_gain_loss}
                                    onChange={handleChange}
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="auto_posted"
                                        checked={formData.auto_posted}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Auto Posted</span>
                                </label>
                            </div>

                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="reversal_created"
                                        checked={formData.reversal_created}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Reversal Created</span>
                                </label>
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
                                    placeholder="Additional notes about this FX revaluation..."
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
                            {loading ? 'Saving...' : (isEditMode ? 'Update FX Revaluation' : 'Create FX Revaluation')}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default FXRevaluationForm;
