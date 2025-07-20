import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProductionDashboard from '../components/production/ProductionDashboard';
import BatchManagement from '../components/production/BatchManagement';
import QualityControl from '../components/production/QualityControl';
import ProductionSchedule from '../components/production/ProductionSchedule';
import MaintenanceLog from '../components/production/MaintenanceLog';
import ProductionAnalytics from '../components/production/ProductionAnalytics';

const ProductionRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<ProductionDashboard />} />
      <Route path="/dashboard" element={<ProductionDashboard />} />
      <Route path="/batches" element={<BatchManagement />} />
      <Route path="/quality" element={<QualityControl />} />
      <Route path="/schedule" element={<ProductionSchedule />} />
      <Route path="/maintenance" element={<MaintenanceLog />} />
      <Route path="/analytics" element={<ProductionAnalytics />} />
    </Routes>
  );
};

export default ProductionRoutes;