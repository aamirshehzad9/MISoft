import React, { useState, useEffect } from 'react';
import productsService from '../../services/productsService';
import './UoMConverter.css';

const UoMConverter = () => {
  const [unitsOfMeasure, setUnitsOfMeasure] = useState([]);
  const [quantity, setQuantity] = useState('');
  const [fromUom, setFromUom] = useState('');
  const [toUom, setToUom] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [availableConversions, setAvailableConversions] = useState([]);

  useEffect(() => {
    fetchUnitsOfMeasure();
  }, []);

  useEffect(() => {
    if (fromUom) {
      fetchAvailableConversions();
    }
  }, [fromUom]);

  const fetchUnitsOfMeasure = async () => {
    try {
      const response = await productsService.listUnitsOfMeasure();
      setUnitsOfMeasure(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching units:', err);
    }
  };

  const fetchAvailableConversions = async () => {
    try {
      const response = await productsService.getAvailableConversions(fromUom);
      setAvailableConversions(response.data.available_conversions || []);
    } catch (err) {
      console.error('Error fetching conversions:', err);
      setAvailableConversions([]);
    }
  };

  const handleConvert = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    if (!quantity || !fromUom || !toUom) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      const response = await productsService.convertUoM({
        quantity: quantity,
        from_uom_id: fromUom,
        to_uom_id: toUom
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Conversion failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSwapUnits = () => {
    const temp = fromUom;
    setFromUom(toUom);
    setToUom(temp);
    setResult(null);
  };

  const getUomName = (id) => {
    const uom = unitsOfMeasure.find(u => u.id === parseInt(id));
    return uom ? `${uom.name} (${uom.symbol})` : '';
  };

  return (
    <div className="uom-converter">
      <div className="converter-header">
        <h2>🔄 Unit of Measure Converter</h2>
        <p>Convert quantities between different units of measure</p>
      </div>

      <div className="converter-body">
        <form onSubmit={handleConvert} className="converter-form">
          <div className="form-row">
            <div className="form-group">
              <label>Quantity</label>
              <input
                type="number"
                step="0.0001"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="Enter quantity"
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>From Unit</label>
              <select
                value={fromUom}
                onChange={(e) => setFromUom(e.target.value)}
                className="form-control"
              >
                <option value="">Select unit...</option>
                {unitsOfMeasure.map(uom => (
                  <option key={uom.id} value={uom.id}>
                    {uom.name} ({uom.symbol}) - {uom.uom_type}
                  </option>
                ))}
              </select>
            </div>

            <div className="swap-button-container">
              <button
                type="button"
                onClick={handleSwapUnits}
                className="btn-swap"
                disabled={!fromUom || !toUom}
                title="Swap units"
              >
                ⇄
              </button>
            </div>

            <div className="form-group">
              <label>To Unit</label>
              <select
                value={toUom}
                onChange={(e) => setToUom(e.target.value)}
                className="form-control"
              >
                <option value="">Select unit...</option>
                {unitsOfMeasure.map(uom => (
                  <option key={uom.id} value={uom.id}>
                    {uom.name} ({uom.symbol}) - {uom.uom_type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !quantity || !fromUom || !toUom}
            >
              {loading ? 'Converting...' : 'Convert'}
            </button>
            <button
              type="button"
              onClick={() => {
                setQuantity('');
                setFromUom('');
                setToUom('');
                setResult(null);
                setError('');
              }}
              className="btn btn-secondary"
            >
              Clear
            </button>
          </div>
        </form>

        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="conversion-result">
            <div className="result-card">
              <h3>Conversion Result</h3>
              <div className="result-display">
                <div className="result-from">
                  <span className="result-value">{quantity}</span>
                  <span className="result-unit">{result.from_uom}</span>
                </div>
                <div className="result-arrow">→</div>
                <div className="result-to">
                  <span className="result-value">{result.converted_quantity}</span>
                  <span className="result-unit">{result.to_uom}</span>
                </div>
              </div>
              <div className="result-details">
                <p><strong>Conversion Type:</strong> {result.conversion_type}</p>
                {result.multiplier && (
                  <p><strong>Multiplier:</strong> {result.multiplier}</p>
                )}
                {result.conversion_rule && (
                  <p><strong>Rule:</strong> {result.conversion_rule}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {fromUom && availableConversions.length > 0 && (
          <div className="available-conversions">
            <h4>Available Conversions from {getUomName(fromUom)}</h4>
            <div className="conversions-list">
              {availableConversions.map((conv) => (
                <div
                  key={conv.id}
                  className="conversion-item"
                  onClick={() => setToUom(conv.to_uom)}
                >
                  <span className="conversion-target">
                    {conv.to_uom_detail.name} ({conv.to_uom_detail.symbol})
                  </span>
                  <span className="conversion-type-badge">
                    {conv.conversion_type_display}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UoMConverter;
