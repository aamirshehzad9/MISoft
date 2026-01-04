import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import accountingService from '../../services/accounting';
import './InvoicesList.css';

const ExchangeRateList = () => {
    const navigate = useNavigate();
    const [exchangeRates, setExchangeRates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchExchangeRates();
    }, []);

    const fetchExchangeRates = async () => {
        try {
            setLoading(true);
            const data = await accountingService.getExchangeRates();
            setExchangeRates(data.results || data);
        } catch (error) {
            console.error('Error fetching exchange rates:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredExchangeRates = exchangeRates.filter(er =>
        er.from_currency_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        er.to_currency_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        er.from_currency_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        er.to_currency_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const columns = [
        { 
            key: 'rate_date', 
            label: 'Date', 
            sortable: true, 
            width: '120px',
            render: (value) => new Date(value).toLocaleDateString()
        },
        { 
            key: 'from_currency_code', 
            label: 'From', 
            sortable: true, 
            width: '100px'
        },
        { 
            key: 'to_currency_code', 
            label: 'To', 
            sortable: true, 
            width: '100px'
        },
        { 
            key: 'exchange_rate', 
            label: 'Exchange Rate', 
            sortable: true, 
            width: '150px',
            render: (value) => parseFloat(value).toFixed(4)
        },
        { 
            key: 'from_currency_name', 
            label: 'From Currency', 
            sortable: true
        },
        { 
            key: 'to_currency_name', 
            label: 'To Currency', 
            sortable: true
        },
    ];

    return (
        <div className="journal-entry-list-page">
            <Card 
                title="Exchange Rates (V2)" 
                subtitle="IAS 21 Compliant Exchange Rate Management"
                action={
                    <Button variant="primary" size="sm" onClick={() => navigate('/dashboard/accounting/exchange-rates/new')}>
                        + New Exchange Rate
                    </Button>
                }
            >
                <div className="invoices-filters">
                    <div className="invoices-search">
                        <Input 
                            placeholder="Search exchange rates..." 
                            value={searchTerm} 
                            onChange={(e) => setSearchTerm(e.target.value)} 
                        />
                    </div>
                </div>
                <Table 
                    columns={columns} 
                    data={filteredExchangeRates} 
                    loading={loading} 
                    emptyMessage="No exchange rates found" 
                    onRowClick={(er) => navigate(`/dashboard/accounting/exchange-rates/${er.id}`)}
                />
            </Card>
        </div>
    );
};

export default ExchangeRateList;
