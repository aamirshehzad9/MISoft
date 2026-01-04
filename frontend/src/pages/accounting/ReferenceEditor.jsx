import React, { useState, useEffect } from 'react';
import accountingService from '../../services/accounting';

const ReferenceEditor = ({ modelName, value = {}, onChange, readOnly = false }) => {
    const [definitions, setDefinitions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDefinitions = async () => {
            try {
                const results = await accountingService.getReferenceDefinitions(modelName);
                if (Array.isArray(results)) {
                     setDefinitions(results);
                } else if (results && results.results) {
                     setDefinitions(results.results);
                } else {
                    setDefinitions([]);
                }
            } catch (error) {
                console.error("Failed to fetch reference definitions", error);
            } finally {
                setLoading(false);
            }
        };

        if (modelName) {
            fetchDefinitions();
        }
    }, [modelName]);

    const handleChange = (key, newValue) => {
        const updated = { ...value, [key]: newValue };
        onChange(updated);
    };

    if (loading) return <div className="text-gray-500 text-sm py-2">Loading custom fields...</div>;
    if (definitions.length === 0) return null;

    return (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mt-4 mb-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded mr-2">Custom</span>
                Additional References
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {definitions.map(def => (
                    <div key={def.id} className="form-group">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            {def.field_label}
                            {def.is_required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        
                        {def.data_type === 'boolean' ? (
                            <div className="flex items-center h-9">
                                <input
                                    type="checkbox"
                                    checked={!!value[def.field_key]}
                                    onChange={(e) => handleChange(def.field_key, e.target.checked)}
                                    disabled={readOnly}
                                    className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                />
                                <span className="ml-2 text-sm text-gray-600">{def.field_label}</span>
                            </div>
                        ) : (
                            <div className="relative">
                                <input
                                    type={def.data_type === 'number' ? 'number' : def.data_type === 'date' ? 'date' : 'text'}
                                    value={value[def.field_key] || ''}
                                    onChange={(e) => handleChange(def.field_key, e.target.value)}
                                    required={def.is_required}
                                    disabled={readOnly}
                                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                    placeholder={def.data_type === 'text' && def.validation_regex ? `Regex: ${def.validation_regex}` : ''}
                                />
                                {def.is_unique && (
                                    <div className="absolute right-0 top-0 -mt-5 mr-1">
                                        <span className="text-[10px] text-orange-600 font-medium bg-orange-50 px-1 rounded">Unique</span>
                                    </div>
                                )}
                            </div>
                        )}
                        {def.data_type === 'text' && def.validation_regex && (
                            <p className="text-xs text-gray-400 mt-1">Format: {def.validation_regex}</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReferenceEditor;
