import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MainLayout from './components/layout/MainLayout';
import PartnersList from './pages/partners/PartnersList';
import PartnerForm from './pages/partners/PartnerForm';
import ProductsList from './pages/products/ProductsList';
import ProductForm from './pages/products/ProductForm';
import ProductionOrdersList from './pages/manufacturing/ProductionOrdersList';
import ProductionOrderForm from './pages/manufacturing/ProductionOrderForm';
import InvoicesList from './pages/accounting/InvoicesList';
import InvoiceForm from './pages/accounting/InvoiceForm';
import PaymentForm from './pages/accounting/PaymentForm';
import ChartOfAccounts from './pages/accounting/ChartOfAccounts';
import VoucherList from './pages/accounting/VoucherList';
import VoucherForm from './pages/accounting/VoucherForm';
import './styles/design-system.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />

        {/* Partners Routes */}
        <Route path="partners">
          <Route index element={<PartnersList />} />
          <Route path="new" element={<PartnerForm />} />
          <Route path=":id" element={<PartnerForm />} />
        </Route>

        {/* Products Routes */}
        <Route path="products">
          <Route index element={<ProductsList />} />
          <Route path="new" element={<ProductForm />} />
          <Route path=":id" element={<ProductForm />} />
        </Route>

        {/* Manufacturing Routes */}
        <Route path="manufacturing">
          <Route index element={<Navigate to="/manufacturing/production-orders" replace />} />
          <Route path="bom" element={<div style={{ padding: '2rem' }}>BOM List - Coming Soon</div>} />
          <Route path="production-orders">
            <Route index element={<ProductionOrdersList />} />
            <Route path="new" element={<ProductionOrderForm />} />
            <Route path=":id" element={<ProductionOrderForm />} />
          </Route>
        </Route>

        {/* Accounting Routes */}
        <Route path="accounting">
          <Route index element={<Navigate to="/accounting/invoices" replace />} />
          <Route path="invoices">
            <Route index element={<InvoicesList />} />
            <Route path="new" element={<InvoiceForm />} />
            <Route path=":id" element={<InvoiceForm />} />
          </Route>
          <Route path="payments">
            <Route index element={<div style={{ padding: '2rem' }}>Payments List - Coming Soon</div>} />
            <Route path="new" element={<PaymentForm />} />
          </Route>
          <Route path="chart-of-accounts" element={<ChartOfAccounts />} />
          <Route path="journal-entries">
            <Route index element={<VoucherList />} />
            <Route path="new" element={<VoucherForm />} />
            <Route path=":id" element={<VoucherForm />} />
          </Route>
          <Route path="vouchers">
            <Route index element={<VoucherList />} />
            <Route path="new" element={<VoucherForm />} />
            <Route path=":id" element={<VoucherForm />} />
          </Route>
        </Route>
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
