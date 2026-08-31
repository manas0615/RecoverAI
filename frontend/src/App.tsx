import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { CaseList } from './pages/CaseList';
import { CaseDetail } from './pages/CaseDetail';
import { ApprovalQueue } from './pages/ApprovalQueue';
import { ExecutionQueue } from './pages/ExecutionQueue';
import { VerificationQueue } from './pages/VerificationQueue';
import { AuditPage } from './pages/AuditPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SystemHealth } from './pages/SystemHealth';
import { FixtureHarness } from './pages/FixtureHarness';

import { NotFound } from './pages/NotFound';

import { ErrorBoundary } from './components/feedback/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/cases" element={<CaseList />} />
          <Route path="/approvals" element={<ApprovalQueue />} />
          <Route path="/execution" element={<ExecutionQueue />} />
          <Route path="/verification" element={<VerificationQueue />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="/fixtures" element={<FixtureHarness />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
    </ErrorBoundary>
  );
}
