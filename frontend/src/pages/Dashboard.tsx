import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ChevronRight, Server } from 'lucide-react';

interface Case {
  case_id: string;
  merchant_id: string;
  customer_id: string;
  status: string;
  amount_minor: number;
  currency: string;
  created_at: string;
  verification_count: number;
}

export default function Dashboard() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState<'healthy' | 'error' | 'loading'>('loading');

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.ok ? setHealth('healthy') : setHealth('error'))
      .catch(() => setHealth('error'));

    fetch('/api/recovery-cases')
      .then(res => res.json())
      .then(data => {
        setCases(data.cases || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const totalAtRisk = cases.reduce((acc, c) => acc + (c.amount_minor / 100), 0);
  const activeCases = cases.filter(c => c.status !== 'CLOSED').length;

  return (
    <div className="p-6 md:p-10 max-w-[1600px] mx-auto space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Overview</h1>
          <p className="text-slate-400 mt-1">Executive summary of revenue recovery operations.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border text-sm">
          <Server size={14} className={health === 'healthy' ? 'text-emerald-400' : 'text-red-400'} />
          <span className="font-medium text-slate-300">
            {health === 'healthy' ? 'System Operational' : health === 'loading' ? 'Checking...' : 'System Degraded'}
          </span>
        </div>
      </header>

      {/* KPI Blocks */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface/40 backdrop-blur-md border border-border p-6 rounded-xl relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Revenue at Risk</h3>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-bold font-mono tracking-tight">${totalAtRisk.toFixed(2)}</span>
            <span className="text-slate-400">USD</span>
          </div>
        </div>
        <div className="bg-surface/40 backdrop-blur-md border border-border p-6 rounded-xl">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Active Cases</h3>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-bold font-mono tracking-tight">{activeCases}</span>
            <span className="text-slate-400">cases</span>
          </div>
        </div>
        <div className="bg-surface/40 backdrop-blur-md border border-border p-6 rounded-xl">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recovery Rate</h3>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-bold font-mono tracking-tight text-emerald-400">68.4%</span>
            <span className="text-emerald-400/80 text-sm font-medium">+2.1%</span>
          </div>
        </div>
      </div>

      {/* Cases List */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-2xl shadow-black/20">
        <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-slate-900/50">
          <h2 className="font-semibold flex items-center gap-2">
            <Activity size={18} className="text-primary" />
            Recent Cases
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="text-slate-400 border-b border-border bg-slate-900/20">
              <tr>
                <th className="px-6 py-3 font-medium">Case ID</th>
                <th className="px-6 py-3 font-medium">Amount</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Created</th>
                <th className="px-6 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400">Loading cases...</td></tr>
              ) : cases.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400">No recovery cases found.</td></tr>
              ) : (
                cases.map(c => (
                  <tr key={c.case_id} className="hover:bg-slate-800/50 transition-colors group">
                    <td className="px-6 py-4 font-mono text-slate-300">{c.case_id.split('_')[1] || c.case_id}</td>
                    <td className="px-6 py-4 font-mono">${(c.amount_minor / 100).toFixed(2)} {c.currency}</td>
                    <td className="px-6 py-4">
                      <span className={'inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ' + (
                        c.status === 'CLOSED' ? 'bg-emerald-500/10 text-emerald-400' :
                        c.status === 'EXECUTING' ? 'bg-blue-500/10 text-blue-400' :
                        'bg-amber-500/10 text-amber-400'
                      )}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">{new Date(c.created_at).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-right">
                      <Link to={'/cases/' + c.case_id} className="inline-flex items-center gap-1 text-primary hover:text-white transition-colors">
                        View <ChevronRight size={16} />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
