import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Button from '../../components/common/Button';
import Input from '../../components/forms/Input';
import Badge from '../../components/common/Badge';
import productsService from '../../services/products';
import './ProductsList.css';

const ProductsList = () => {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');

    useEffect(() => {
        fetchProducts();
    }, [filterType]);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            let data;
            if (filterType === 'raw_materials') {
                data = await productsService.getRawMaterials();
            } else if (filterType === 'finished_goods') {
                data = await productsService.getFinishedGoods();
            } else {
                data = await productsService.getAll();
            }
            setProducts(data);
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredProducts = products.filter(product =>
        product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.code?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getProductTypeBadge = (type) => {
        const badges = {
            raw_material: { variant: 'info', label: 'Raw Material' },
            finished_good: { variant: 'success', label: 'Finished Good' },
            semi_finished: { variant: 'warning', label: 'Semi-Finished' },
            consumable: { variant: 'default', label: 'Consumable' },
        };
        return badges[type] || { variant: 'default', label: type };
    };

    const columns = [
        {
            key: 'code',
            label: 'Code',
            sortable: true,
            width: '120px',
        },
        {
            key: 'name',
            label: 'Product Name',
            sortable: true,
            render: (value, row) => (
                <div className="product-name-cell">
                    <strong>{value}</strong>
                    {row.category_name && <div className="product-category">{row.category_name}</div>}
                </div>
            ),
        },
        {
            key: 'product_type',
            label: 'Type',
            render: (value) => {
                const badge = getProductTypeBadge(value);
                return <Badge variant={badge.variant} size="sm">{badge.label}</Badge>;
            },
        },
        {
            key: 'base_uom_symbol',
            label: 'UOM',
            width: '80px',
        },
        {
            key: 'standard_cost',
            label: 'Cost',
            sortable: true,
            render: (value) => `PKR ${parseFloat(value || 0).toLocaleString()}`,
        },
        {
            key: 'selling_price',
            label: 'Price',
            sortable: true,
            render: (value) => `PKR ${parseFloat(value || 0).toLocaleString()}`,
        },
        {
            key: 'is_active',
            label: 'Status',
            render: (value) => (
                <Badge variant={value ? 'success' : 'danger'} size="sm">
                    {value ? 'Active' : 'Inactive'}
                </Badge>
            ),
        },
    ];

    return (
        <div className="products-list-page">
            <Card
                title="Products & Inventory"
                subtitle="Manage products, raw materials, and finished goods"
                actions={
                    <Button
                        variant="primary"
                        onClick={() => navigate('/dashboard/products/new')}
                        icon={
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                        }
                    >
                        Add Product
                    </Button>
                }
            >
                <div className="products-filters">
                    <div className="products-search">
                        <Input
                            placeholder="Search by name or code..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            icon={
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10zM14 14l-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            }
                        />
                    </div>
                    <div className="products-filter-buttons">
                        <Button
                            variant={filterType === 'all' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('all')}
                        >
                            All Products
                        </Button>
                        <Button
                            variant={filterType === 'raw_materials' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('raw_materials')}
                        >
                            Raw Materials
                        </Button>
                        <Button
                            variant={filterType === 'finished_goods' ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setFilterType('finished_goods')}
                        >
                            Finished Goods
                        </Button>
                    </div>
                </div>

                <Table
                    columns={columns}
                    data={filteredProducts}
                    loading={loading}
                    emptyMessage="No products found"
                    onRowClick={(row) => navigate(`/products/${row.id}`)}
                />
            </Card>
        </div>
    );
};

export default ProductsList;
