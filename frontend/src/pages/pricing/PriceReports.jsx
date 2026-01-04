import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Table from '../../components/common/Table';
import pricingService from '../../services/pricingService';
import productsService from '../../services/products';
import partnersService from '../../services/partners';

const PriceReports = () => {
  const [activeReport, setActiveReport] = useState('by_product');
  const [reportData, setReportData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  
  // Filters
  const [filters, setFilters] = useState({
    product_id: '',
    customer_id: '',
    date: new Date().toISOString().split('T')[0],
    days: 90,
    active_only: true
  });

  useEffect(() => {
    loadDropdowns();
  }, []);

  useEffect(() => {
    if (activeReport) {
      loadReport();
    }
  }, [activeReport]);

  const loadDropdowns = async () => {
    try {
      const [prods, custs] = await Promise.all([
        productsService.getAll(),
        partnersService.getAll()
      ]);
      setProducts(prods.results || prods);
      setCustomers(custs.results || custs);
    } catch (err) {
      console.error('Error loading dropdowns:', err);
    }
  };

  const loadReport = async () => {
    setLoading(true);
    try {
      let response;
      const params = {};
      
      switch (activeReport) {
        case 'by_product':
          if (filters.product_id) params.product_id = filters.product_id;
          if (filters.date) params.date = filters.date;
          params.active_only = filters.active_only;
          response = await pricingService.getReportByProduct(params);
          break;
          
        case 'by_customer':
          if (filters.customer_id) params.customer_id = filters.customer_id;
          if (filters.date) params.date = filters.date;
          params.active_only = filters.active_only;
          response = await pricingService.getReportByCustomer(params);
          break;
          
        case 'price_history':
          if (filters.product_id) params.product_id = filters.product_id;
          if (filters.customer_id) params.customer_id = filters.customer_id;
          params.days = filters.days;
          response = await pricingService.getReportPriceHistory(params);
          break;
          
        case 'price_variance':
          if (filters.date) params.date = filters.date;
          response = await pricingService.getReportPriceVariance(params);
          break;
          
        default:
          return;
      }
      
      setReportData(response.data.data || []);
    } catch (err) {
      console.error('Error loading report:', err);
      alert('Error loading report: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getColumns = () => {
    switch (activeReport) {
      case 'by_product':
        return [
          { key: 'product_code', label: 'Product Code' },
          { key: 'product_name', label: 'Product Name' },
          { key: 'rule_name', label: 'Rule' },
          { key: 'customer', label: 'Customer' },
          { key: 'priority', label: 'Priority' },
          { key: 'price', label: 'Price', render: (row) => row.price ? `PKR ${row.price}` : `${row.discount_percentage}% Off` },
          { key: 'valid_from', label: 'Valid From' },
          { key: 'valid_to', label: 'Valid To' }
        ];
        
      case 'by_customer':
        return [
          { key: 'customer_name', label: 'Customer' },
          { key: 'product_code', label: 'Product Code' },
          { key: 'product_name', label: 'Product Name' },
          { key: 'rule_name', label: 'Rule' },
          { key: 'priority', label: 'Priority' },
          { key: 'price', label: 'Price', render: (row) => row.price ? `PKR ${row.price}` : `${row.discount_percentage}% Off` },
          { key: 'valid_from', label: 'Valid From' }
        ];
        
      case 'price_history':
        return [
          { key: 'product_code', label: 'Product' },
          { key: 'customer', label: 'Customer' },
          { key: 'rule_name', label: 'Rule' },
          { key: 'price', label: 'Price', render: (row) => row.price ? `PKR ${row.price}` : `${row.discount_percentage}% Off` },
          { key: 'effective_from', label: 'From' },
          { key: 'effective_to', label: 'To' },
          { key: 'days_active', label: 'Days Active' }
        ];
        
      case 'price_variance':
        return [
          { key: 'product_code', label: 'Product' },
          { key: 'rule_name', label: 'Rule' },
          { key: 'customer', label: 'Customer' },
          { key: 'base_price', label: 'Base Price', render: (row) => `PKR ${row.base_price}` },
          { key: 'effective_price', label: 'Effective Price', render: (row) => `PKR ${row.effective_price}` },
          { key: 'variance_amount', label: 'Variance', render: (row) => `PKR ${row.variance_amount}` },
          { key: 'variance_percentage', label: 'Variance %', render: (row) => `${row.variance_percentage}%` }
        ];
        
      default:
        return [];
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Price Reports</h1>
      </div>

      {/* Report Type Selector */}
      <Card title="Select Report Type">
        <div className="flex gap-2 flex-wrap">
          <Button 
            variant={activeReport === 'by_product' ? 'primary' : 'outline'}
            onClick={() => setActiveReport('by_product')}
          >
            By Product
          </Button>
          <Button 
            variant={activeReport === 'by_customer' ? 'primary' : 'outline'}
            onClick={() => setActiveReport('by_customer')}
          >
            By Customer
          </Button>
          <Button 
            variant={activeReport === 'price_history' ? 'primary' : 'outline'}
            onClick={() => setActiveReport('price_history')}
          >
            Price History
          </Button>
          <Button 
            variant={activeReport === 'price_variance' ? 'primary' : 'outline'}
            onClick={() => setActiveReport('price_variance')}
          >
            Price Variance
          </Button>
        </div>
      </Card>

      {/* Filters */}
      <Card title="Filters">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {(activeReport === 'by_product' || activeReport === 'price_history') && (
            <div>
              <label className="block text-sm font-medium mb-1">Product</label>
              <select 
                className="w-full border p-2 rounded"
                value={filters.product_id}
                onChange={(e) => setFilters({...filters, product_id: e.target.value})}
              >
                <option value="">All Products</option>
                {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
          )}
          
          {(activeReport === 'by_customer' || activeReport === 'price_history') && (
            <div>
              <label className="block text-sm font-medium mb-1">Customer</label>
              <select 
                className="w-full border p-2 rounded"
                value={filters.customer_id}
                onChange={(e) => setFilters({...filters, customer_id: e.target.value})}
              >
                <option value="">All Customers</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
          )}
          
          {activeReport !== 'price_history' && (
            <div>
              <label className="block text-sm font-medium mb-1">Date</label>
              <input 
                type="date"
                className="w-full border p-2 rounded"
                value={filters.date}
                onChange={(e) => setFilters({...filters, date: e.target.value})}
              />
            </div>
          )}
          
          {activeReport === 'price_history' && (
            <div>
              <label className="block text-sm font-medium mb-1">Days</label>
              <input 
                type="number"
                className="w-full border p-2 rounded"
                value={filters.days}
                onChange={(e) => setFilters({...filters, days: e.target.value})}
              />
            </div>
          )}
          
          <div className="flex items-end">
            <Button onClick={loadReport}>Generate Report</Button>
          </div>
        </div>
      </Card>

      {/* Report Data */}
      <Card title={`Report: ${activeReport.replace('_', ' ').toUpperCase()}`}>
        <div className="mb-4 text-sm text-gray-600">
          Total Records: {reportData.length}
        </div>
        <Table 
          columns={getColumns()}
          data={reportData}
          isLoading={loading}
        />
      </Card>
    </div>
  );
};

export default PriceReports;
