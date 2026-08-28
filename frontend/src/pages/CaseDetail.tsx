import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft, ShieldAlert, Cpu, GitPullRequest, CheckCircle2, Clock, Play } from 'lucide-react';

interface CaseDetail {
  case_id: string;
  amount_minor: number;
  currency: string;
  status: string;
  created_at: string;
}

export default function CaseDetail() {
  const { id } = useParams();
  const [data, setData] = useState<CaseDetail | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/recovery-cases/' + id).then(res => res.json()),
      fetch('/api/recovery-cases/' + id + '/timeline').then(res => res.json())
    ]).then(([caseData, timelineData]) => {
      setData(caseData);
      setTimeline(timelineData.events || []);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <div className="p-10 text-slate-400">Loading case details...</div>;
  if (!data) return <div className="p-10 text-red-400">Case not found.</div>;

  return (
    <div className="p-6 md:p-10 max-w-[1600px] mx-auto space-y-8 animate-in fade-in duration-500">
      <header className="flex items-center gap-4 border-b border-border pb-6">
        <Link to="/" className="p-2 rounded-md bg-surface border border-border hover:bg-slate-800 transition-colors">
          <ChevronLeft size={20} />
        </Link>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold font-mono tracking-tight">Case {data.case_id.split('_')[1] || data.case_id}</h1>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {data.status}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">Created on {new Date(data.created_at).toLocaleString()}</p>
        </div>
      </header>

      {/* Tri-Fold Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* 1. AI Intelligence */}
        <div className="bg-surface/50 border border-border rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-border bg-slate-800/30 flex items-center gap-2">
            <Cpu className="text-primary" size={18} />
            <h2 className="font-semibold text-sm uppercase tracking-wider text-slate-300">AI Intelligence</h2>
          </div>
          <div className="p-6 flex-1 space-y-6">
            <div>
              <p className="text-sm text-slate-400 mb-1">Amount at Risk</p>
              <p className="text-4xl font-bold font-mono text-white">${(data.amount_minor / 100).toFixed(2)}</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/50">
              <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">Root Cause Analysis</h3>
              <p className="text-sm text-slate-300">High confidence of 'Insufficient Funds'. Payment velocity has dropped 40% in last 2 billing cycles.</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Recommended Intervention</p>
              <div className="inline-flex items-center gap-2 text-sm font-medium text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
                <CheckCircle2 size={16} /> Create Payment Link
              </div>
            </div>
          </div>
        </div>

        {/* 2. Policy Decision */}
        <div className="bg-surface/50 border border-border rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-border bg-slate-800/30 flex items-center gap-2">
            <ShieldAlert className="text-purple-400" size={18} />
            <h2 className="font-semibold text-sm uppercase tracking-wider text-slate-300">Policy Decision</h2>
          </div>
          <div className="p-6 flex-1 space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 grid place-items-center shrink-0">
                <CheckCircle2 size={18} />
              </div>
              <div>
                <h3 className="font-medium text-slate-200">Action Authorized</h3>
                <p className="text-sm text-slate-400 mt-1">Intervention complies with merchant rules. Value is below $500 manual-review threshold.</p>
              </div>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/50 space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Rule: Max Retries</span>
                <span className="text-emerald-400 font-medium">PASS</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Rule: Fraud Check</span>
                <span className="text-emerald-400 font-medium">PASS</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Execution Hub */}
        <div className="bg-surface/50 border border-primary/30 rounded-xl overflow-hidden flex flex-col relative shadow-[0_0_20px_rgba(0,122,255,0.1)]">
          <div className="p-4 border-b border-primary/20 bg-primary/5 flex items-center gap-2">
            <GitPullRequest className="text-primary" size={18} />
            <h2 className="font-semibold text-sm uppercase tracking-wider text-primary">Execution Hub</h2>
          </div>
          <div className="p-6 flex-1 flex flex-col justify-between">
            <div className="space-y-4">
              <h3 className="font-medium text-slate-200">Execution Status</h3>
              <div className="flex items-center gap-3">
                <div className="relative flex items-center justify-center">
                  <div className="w-4 h-4 bg-primary rounded-full animate-ping absolute opacity-50" />
                  <div className="w-3 h-3 bg-primary rounded-full relative" />
                </div>
                <span className="text-sm font-medium text-slate-300">Waiting for Trigger...</span>
              </div>
            </div>
            
            <button className="mt-8 w-full py-3 px-4 bg-primary hover:bg-blue-600 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors border border-blue-400/50 shadow-lg shadow-primary/20">
              <Play size={18} />
              Execute Intervention
            </button>
          </div>
        </div>

      </div>

      {/* Audit Timeline */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-border bg-slate-900/50 flex items-center gap-2">
          <Clock size={18} className="text-slate-400" />
          <h2 className="font-semibold text-sm uppercase tracking-wider text-slate-300">Audit Timeline</h2>
        </div>
        <div className="p-6">
          {timeline.length === 0 ? (
            <p className="text-slate-400 text-sm">No timeline events recorded.</p>
          ) : (
            <div className="space-y-6">
              {timeline.map((event, i) => (
                <div key={i} className="flex gap-4 relative">
                  {i !== timeline.length - 1 && <div className="absolute top-6 bottom-[-24px] left-[11px] w-px bg-border" /> }
                  <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-600 grid place-items-center shrink-0 z-10">
                    <div className="w-2 h-2 rounded-full bg-slate-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-200">{event.event_type}</p>
                    <p className="text-xs text-slate-500 mt-1">{new Date(event.timestamp).toLocaleString()}</p>
                    {event.details && <pre className="mt-2 text-xs bg-slate-900/50 p-2 rounded text-slate-400 border border-slate-800/50">{JSON.stringify(event.details, null, 2)}</pre>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
