import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { CaseList } from './pages/CaseList';
import { CaseDetail } from './pages/CaseDetail';
import { SystemHealth } from './pages/SystemHealth';
import { FixtureHarness } from './pages/FixtureHarness';

import { NotFound } from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/cases" element={<CaseList />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="/fixtures" element={<FixtureHarness />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
