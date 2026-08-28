import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { CaseList } from './pages/CaseList';
import { CaseDetail } from './pages/CaseDetail';
import { SystemHealth } from './pages/SystemHealth';

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/cases" element={<CaseList />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="/activity" element={
            <div className="flex flex-col items-center justify-center p-12 text-center h-[50vh]">
              <h2 className="text-xl font-display font-bold text-[var(--color-text-primary)] mb-2">Activity Log</h2>
              <p className="text-[var(--color-text-secondary)]">This feature is coming soon.</p>
            </div>
          } />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
