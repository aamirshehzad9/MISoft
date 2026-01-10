import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import pricingService from '../../services/pricingService';
import productsService from '../../services/products';
import partnersService from '../../services/partners';

const PriceMatrix = () => {
  const [activeTab, setActiveTab] = useState('rules');
  const [rules, setRules] = useState([]);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Simulation State
  const [simForm, setSimForm] = useState({ 
    product_id: '', 
    customer_id: '', 
    quantity: 1, 
    date: new Date().toISOString().split('T')[0] 
  });
  const [simResult, setSimResult] = useState(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [rulesRes, prods, custs] = await Promise.all([
        pricingService.getRules(),
        productsService.getAll(),
        partnersService.getAll()
      ]);
      // Axios already extracts .data, so rulesRes is the response data
      // API returns paginated response: {count, next, previous, results: []}
      setRules(Array.isArray(rulesRes) ? rulesRes : (rulesRes?.results || []));
      setProducts(Array.isArray(prods) ? prods : (prods?.results || []));
      setCustomers(Array.isArray(custs) ? custs : (custs?.results || []));
    } catch (error) {
      console.error("Error loading data", error);
      // Set empty arrays on error to prevent crashes
      setRules([]);
      setProducts([]);
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async (e) => {
    e.preventDefault();
    if (!simForm.product_id) return alert('Please select a product');
    
    try {
      const res = await pricingService.calculatePrice(simForm);
      setSimResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await pricingService.exportTemplate();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'price_rules_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert('Error downloading template: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleFileImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      const res = await pricingService.bulkImport(file);
      const data = res.data;
      
      if (data.errors && data.errors.length > 0) {
        alert(`Import completed with warnings:\nCreated: ${data.created_count}/${data.total_rows}\n\nErrors:\n${data.errors.join('\n')}`);
      } else {
        alert(`Successfully imported ${data.created_count} price rules!`);
      }
      
      // Refresh rules list
      fetchInitialData();
      e.target.value = ''; // Reset file input
    } catch (err) {
      console.error(err);
      alert('Import failed: ' + (err.response?.data?.error || err.message));
      e.target.value = '';
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: 'rule_name', label: 'Rule Name' },
    { key: 'product_name', label: 'Product' },
    { key: 'priority', label: 'Priority' },
    { key: 'valid_from', label: 'Valid From' },
    { key: 'valid_to', label: 'Valid To' },
    { 
      key: 'price', 
      label: 'Price/Discount',
      render: (value, row) => row.price > 0 ? `PKR ${row.price}` : `${row.discount_percentage}% Off`
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (value, row) => <Badge variant={row.is_active ? 'success' : 'danger'}>{row.is_active ? 'Active' : 'Inactive'}</Badge>
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Price Management</h1>
        <div className="space-x-2">
            <Button variant={activeTab === 'rules' ? 'primary' : 'outline'} onClick={() => setActiveTab('rules')}>Rules</Button>
            <Button variant={activeTab === 'simulate' ? 'primary' : 'outline'} onClick={() => setActiveTab('simulate')}>Simulation</Button>
        </div>
      </div>

      {activeTab === 'rules' && (
        <Card title="Pricing Rules">
            <div className="mb-4 flex gap-2">
                <Button>Add Rule</Button>
                <Button variant="outline" onClick={handleDownloadTemplate}>Download Template</Button>
                <label className="inline-block">
                    <Button variant="outline" as="span">Import Rules</Button>
                    <input 
                        type="file" 
                        accept=".csv,.xlsx,.xls" 
                        onChange={handleFileImport}
                        className="hidden"
                    />
                </label>
            </div>
            <Table 
                columns={columns} 
                data={rules} 
                isLoading={loading}
            />
        </Card>
      )}

      {activeTab === 'simulate' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Simulation Parameters">
                <form onSubmit={handleSimulate} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium">Product</label>
                        <select 
                            className="w-full border p-2 rounded"
                            value={simForm.product_id}
                            onChange={(e) => setSimForm({...simForm, product_id: e.target.value})}
                        >
                            <option value="">Select Product</option>
                            {products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.code})</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Customer</label>
                        <select 
                            className="w-full border p-2 rounded"
                            value={simForm.customer_id}
                            onChange={(e) => setSimForm({...simForm, customer_id: e.target.value})}
                        >
                            <option value="">Any/None</option>
                            {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Quantity</label>
                        <input 
                            type="number" 
                            className="w-full border p-2 rounded"
                            value={simForm.quantity}
                            onChange={(e) => setSimForm({...simForm, quantity: e.target.value})}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Date</label>
                        <input 
                            type="date" 
                            className="w-full border p-2 rounded"
                            value={simForm.date}
                            onChange={(e) => setSimForm({...simForm, date: e.target.value})}
                        />
                    </div>
                    <Button type="submit">Calculate Price</Button>
                </form>
            </Card>

            {simResult && (
                <Card title="Calculation Result">
                    <div className="space-y-4">
                        <div className="flex justify-between border-b pb-2">
                            <span>Original Price:</span>
                            <span className="font-bold">{simResult.original_price} {simResult.currency}</span>
                        </div>
                        <div className="flex justify-between border-b pb-2">
                            <span>Quantity:</span>
                            <span>{simResult.quantity}</span>
                        </div>
                         <div className="flex justify-between border-b pb-2">
                            <span>Applied Rule:</span>
                            <Badge variant={simResult.applied_rule ? 'info' : 'secondary'}>
                                {simResult.applied_rule || 'Base Price'}
                            </Badge>
                        </div>
                        <div className="flex justify-between text-xl mt-4">
                            <span>Final Price (Unit):</span>
                            <span className="font-bold text-green-600">{simResult.final_price} {simResult.currency}</span>
                        </div>
                         <div className="flex justify-between text-xl">
                            <span>Total:</span>
                            <span className="font-bold text-green-600">
                                {(parseFloat(simResult.final_price) * parseFloat(simResult.quantity)).toFixed(2)} {simResult.currency}
                            </span>
                        </div>
                    </div>
                </Card>
            )}
        </div>
      )}
    </div>
  );
};

export default PriceMatrix;
