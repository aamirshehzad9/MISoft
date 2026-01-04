import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Select from '../../components/forms/Select';
import partnersService from '../../services/partners';
import './PartnerForm.css';

const PartnerForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = Boolean(id);

    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        company_name: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        state: '',
        country: 'Pakistan',
        postal_code: '',
        is_customer: false,
        is_vendor: false,
        credit_limit: 0,
        payment_terms: '',
        tax_id: '',
        notes: '',
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (isEdit) {
            fetchPartner();
        }
    }, [id]);

    const fetchPartner = async () => {
        try {
            const data = await partnersService.getById(id);
            setFormData(data);
        } catch (error) {
            console.error('Error fetching partner:', error);
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
        if (!formData.name.trim()) newErrors.name = 'Name is required';
        if (!formData.email.trim()) newErrors.email = 'Email is required';
        if (!formData.is_customer && !formData.is_vendor) {
            newErrors.type = 'Select at least Customer or Vendor';
        }
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const newErrors = validate();

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            setLoading(true);
            if (isEdit) {
                await partnersService.update(id, formData);
            } else {
                await partnersService.create(formData);
            }
            navigate('/dashboard/partners');
        } catch (error) {
            console.error('Error saving partner:', error);
            setErrors({ submit: 'Failed to save partner. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="partner-form-page">
            <Card
                title={isEdit ? 'Edit Partner' : 'New Partner'}
                subtitle={isEdit ? 'Update partner information' : 'Add a new business partner'}
            >
                <form onSubmit={handleSubmit} className="partner-form">
                    {errors.submit && (
                        <div className="form-error-message">{errors.submit}</div>
                    )}

                    <div className="form-section">
                        <h3 className="form-section-title">Basic Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                error={errors.name}
                                required
                            />
                            <Input
                                label="Company Name"
                                name="company_name"
                                value={formData.company_name}
                                onChange={handleChange}
                            />
                            <Input
                                label="Email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                                error={errors.email}
                                required
                            />
                            <Input
                                label="Phone"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Partner Type</h3>
                        <div className="checkbox-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="is_customer"
                                    checked={formData.is_customer}
                                    onChange={handleChange}
                                />
                                <span>Customer</span>
                            </label>
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="is_vendor"
                                    checked={formData.is_vendor}
                                    onChange={handleChange}
                                />
                                <span>Vendor</span>
                            </label>
                        </div>
                        {errors.type && <span className="input-error-text">{errors.type}</span>}
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Address</h3>
                        <div className="form-grid">
                            <Input
                                label="Address"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                className="form-grid-full"
                            />
                            <Input
                                label="City"
                                name="city"
                                value={formData.city}
                                onChange={handleChange}
                            />
                            <Input
                                label="State/Province"
                                name="state"
                                value={formData.state}
                                onChange={handleChange}
                            />
                            <Input
                                label="Country"
                                name="country"
                                value={formData.country}
                                onChange={handleChange}
                            />
                            <Input
                                label="Postal Code"
                                name="postal_code"
                                value={formData.postal_code}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="form-section">
                        <h3 className="form-section-title">Financial Information</h3>
                        <div className="form-grid">
                            <Input
                                label="Credit Limit"
                                name="credit_limit"
                                type="number"
                                value={formData.credit_limit}
                                onChange={handleChange}
                            />
                            <Input
                                label="Payment Terms"
                                name="payment_terms"
                                value={formData.payment_terms}
                                onChange={handleChange}
                                helperText="e.g., Net 30, Net 60"
                            />
                            <Input
                                label="Tax ID / NTN"
                                name="tax_id"
                                value={formData.tax_id}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => navigate('/dashboard/partners')}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="primary"
                            loading={loading}
                        >
                            {isEdit ? 'Update Partner' : 'Create Partner'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default PartnerForm;
