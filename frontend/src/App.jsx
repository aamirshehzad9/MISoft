import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import LandingPage from './pages/LandingPage';
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
import NumberingSchemesList from './pages/accounting/NumberingSchemesList';
import Cheques from './pages/accounting/Cheques';
import BankTransfers from './pages/accounting/BankTransfers';
import BankReconciliation from './pages/accounting/BankReconciliation';
import AuditTrail from './pages/accounting/AuditTrail';
import FixedAssetsList from './pages/accounting/FixedAssetsList';
import FixedAssetsReports from './pages/accounting/FixedAssetsReports';
import FiscalYearList from './pages/accounting/FiscalYearList';
import FiscalYearForm from './pages/accounting/FiscalYearForm';
import TaxCodeList from './pages/accounting/TaxCodeList';
import TaxCodeForm from './pages/accounting/TaxCodeForm';
import TaxMasterList from './pages/accounting/TaxMasterList';
import TaxMasterForm from './pages/accounting/TaxMasterForm';
import TaxGroupList from './pages/accounting/TaxGroupList';
import TaxGroupForm from './pages/accounting/TaxGroupForm';
import CurrencyList from './pages/accounting/CurrencyList';
import CurrencyForm from './pages/accounting/CurrencyForm';
import ExchangeRateList from './pages/accounting/ExchangeRateList';
import ExchangeRateForm from './pages/accounting/ExchangeRateForm';
import CostCenterList from './pages/accounting/CostCenterList';
import CostCenterForm from './pages/accounting/CostCenterForm';
import DepartmentList from './pages/accounting/DepartmentList';
import DepartmentForm from './pages/accounting/DepartmentForm';
import EntityList from './pages/accounting/EntityList';
import EntityForm from './pages/accounting/EntityForm';
import BankAccountList from './pages/accounting/BankAccountList';
import BankAccountForm from './pages/accounting/BankAccountForm';
import BankStatementList from './pages/accounting/BankStatementList';
import BankStatementForm from './pages/accounting/BankStatementForm';
import FairValueList from './pages/accounting/FairValueList';
import FairValueForm from './pages/accounting/FairValueForm';
import FXRevaluationList from './pages/accounting/FXRevaluationList';
import FXRevaluationForm from './pages/accounting/FXRevaluationForm';
import PriceMatrix from './pages/pricing/PriceMatrix';
import PriceReports from './pages/pricing/PriceReports';
import UoMConverter from './pages/products/UoMConverter';
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

// Public Route Component (redirects to dashboard if logged in)
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
      <Route path="/" element={<LandingPage />} />

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
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />

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
          <Route index element={<Navigate to="/dashboard/manufacturing/production-orders" replace />} />
          <Route path="bom" element={<div style={{ padding: '2rem' }}>BOM List - Coming Soon</div>} />
          <Route path="production-orders">
            <Route index element={<ProductionOrdersList />} />
            <Route path="new" element={<ProductionOrderForm />} />
            <Route path=":id" element={<ProductionOrderForm />} />
          </Route>
        </Route>

        {/* Accounting Routes */}
        <Route path="accounting">
          <Route index element={<Navigate to="/dashboard/accounting/invoices" replace />} />
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
          <Route path="cheques" element={<Cheques />} />
          <Route path="bank-transfers" element={<BankTransfers />} />
          <Route path="bank-reconciliation" element={<BankReconciliation />} />
          <Route path="fixed-assets">
            <Route index element={<FixedAssetsList />} />
            <Route path="reports" element={<FixedAssetsReports />} />
          </Route>
          <Route path="fiscal-years">
            <Route index element={<FiscalYearList />} />
            <Route path="new" element={<FiscalYearForm />} />
            <Route path=":id" element={<FiscalYearForm />} />
          </Route>
          <Route path="tax-codes">
            <Route index element={<TaxCodeList />} />
            <Route path="new" element={<TaxCodeForm />} />
            <Route path=":id" element={<TaxCodeForm />} />
          </Route>
          <Route path="tax-masters">
            <Route index element={<TaxMasterList />} />
            <Route path="new" element={<TaxMasterForm />} />
            <Route path=":id" element={<TaxMasterForm />} />
          </Route>
          <Route path="tax-groups">
            <Route index element={<TaxGroupList />} />
            <Route path="new" element={<TaxGroupForm />} />
            <Route path=":id" element={<TaxGroupForm />} />
          </Route>
          <Route path="currencies">
            <Route index element={<CurrencyList />} />
            <Route path="new" element={<CurrencyForm />} />
            <Route path=":id" element={<CurrencyForm />} />
          </Route>
          <Route path="exchange-rates">
            <Route index element={<ExchangeRateList />} />
            <Route path="new" element={<ExchangeRateForm />} />
            <Route path=":id" element={<ExchangeRateForm />} />
          </Route>
          <Route path="cost-centers">
            <Route index element={<CostCenterList />} />
            <Route path="new" element={<CostCenterForm />} />
            <Route path=":id" element={<CostCenterForm />} />
          </Route>
          <Route path="departments">
            <Route index element={<DepartmentList />} />
            <Route path="new" element={<DepartmentForm />} />
            <Route path=":id" element={<DepartmentForm />} />
          </Route>
          <Route path="entities">
            <Route index element={<EntityList />} />
            <Route path="new" element={<EntityForm />} />
            <Route path=":id" element={<EntityForm />} />
          </Route>
          <Route path="bank-accounts">
            <Route index element={<BankAccountList />} />
            <Route path="new" element={<BankAccountForm />} />
            <Route path=":id" element={<BankAccountForm />} />
          </Route>
          <Route path="bank-statements">
            <Route index element={<BankStatementList />} />
            <Route path="new" element={<BankStatementForm />} />
            <Route path=":id" element={<BankStatementForm />} />
          </Route>
          <Route path="fair-value-measurements">
            <Route index element={<FairValueList />} />
            <Route path="new" element={<FairValueForm />} />
            <Route path=":id" element={<FairValueForm />} />
          </Route>
          <Route path="fx-revaluation-logs">
            <Route index element={<FXRevaluationList />} />
            <Route path="new" element={<FXRevaluationForm />} />
            <Route path=":id" element={<FXRevaluationForm />} />
          </Route>
          <Route path="audit-trail" element={<AuditTrail />} />
          <Route path="numbering-schemes" element={<NumberingSchemesList />} />
        </Route>

        {/* Pricing Routes */}
        <Route path="pricing" element={<PriceMatrix />} />
        
        {/* Products Routes */}
        <Route path="uom-converter" element={<UoMConverter />} />
      </Route>

      {/* Catch all - redirect to landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
