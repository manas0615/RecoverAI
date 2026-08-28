import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Activity, LayoutDashboard, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import CaseDetail from './pages/CaseDetail';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-background overflow-hidden selection:bg-primary/30">
        {/* Sidebar */}
        <nav className="w-64 border-r border-border bg-surface/50 backdrop-blur-xl flex flex-col hidden md:flex">
          <div className="p-6">
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-primary grid place-items-center">
                <div className="w-3 h-3 rounded-full bg-white" />
              </div>
              RecoverAI
            </h1>
          </div>
          <div className="flex-1 px-4 py-2 space-y-1">
            <Link to="/" className="flex items-center gap-3 px-3 py-2 rounded-md bg-primary/10 text-primary font-medium text-sm">
              <LayoutDashboard size={18} />
              Dashboard
            </Link>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors font-medium text-sm">
              <Activity size={18} />
              Recovery Cases
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors font-medium text-sm">
              <Settings size={18} />
              Settings
            </a>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto relative">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases/:id" element={<CaseDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
