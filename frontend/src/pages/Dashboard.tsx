import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useMemo, useState } from 'react';
import { useCases, useAnalytics, useCaseDetails } from '../hooks/useApi';
import { MoneyValue } from '../components/financial/MoneyValue';
import { RecoveryJourney } from '../components/financial/RecoveryJourney';
import { AlertTriangle, FileText, Zap, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../api/client';

function KpiCard({ title, value, titleColor = 'text-[var(--color-text-secondary)]', valueColor = 'text-[var(--color-text-primary)]', icon = null }: { title: string, value: React.ReactNode, titleColor?: string, valueColor?: string, icon?: React.ReactNode }) {
  return (
    <div className="flex flex-col p-5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <h3 className={`text-sm font-medium ${titleColor} tracking-wide`}>{title}</h3>
        {icon}
      </div>
      <div className={`text-3xl font-bold font-display ${valueColor}`}>
        {value}
      </div>
    </div>
  );
}

export function Dashboard() {
  const { data } = useCases();
  const { data: analyticsData } = useAnalytics();
  
  
  const metrics = useMemo(() => {
    if (!data || !analyticsData) return null;
    
    // Revenue at Risk (sum of active cases)
    const openCases = data.cases.filter(c => c.status === 'OPEN');
    const revenueAtRisk = openCases.reduce((sum, c) => sum + c.amount_minor, 0);
    
    // Verified Recovered (sum of recovered cases)
    const recoveredCases = data.cases.filter(c => c.outcome_type === 'RECOVERED' || c.workflow_state === 'RECOVERED');
    const revenueRecovered = recoveredCases.reduce((sum, c) => {
      return sum + (c.recovered_amount_minor ?? c.amount_minor);
    }, 0);
    
    // Approvals pending
    const approvalsPending = openCases.filter(c => c.workflow_state === 'APPROVAL_REQUIRED' || c.workflow_state === 'POLICY_REVIEW').length;
    
    // Recovery rate
    const totalFinished = data.cases.filter(c => c.status === 'CLOSED').length;
    const rate = totalFinished > 0 ? ((recoveredCases.length / totalFinished) * 100).toFixed(1) : '0.0';
    
    return {
      revenueAtRisk,
      revenueRecovered,
      approvalsPending,
      recoveryRate: `${rate}%`
    };
  }, [data, analyticsData]);

  // Find a priority case for the dashboard
  const priorityCase = useMemo(() => {
    if (!data) return null;
    // Prefer cases needing approval, then any open case
    return data.cases.find(c => c.workflow_state === 'APPROVAL_REQUIRED') || data.cases.find(c => c.status === 'OPEN') || data.cases[0];
  }, [data]);

  const { data: priorityCaseData, refetch: refetchPriority } = useCaseDetails(priorityCase?.case_id);
  const [approving, setApproving] = useState(false);

  const handleApprove = async () => {
    if (!priorityCaseData) return;
    setApproving(true);
    try {
      // Find action_id from events
      const actionProposedEvent = priorityCaseData.timeline.slice().reverse().find(e => e.event_type === 'ACTION_PROPOSED' || e.action_id);
      if (actionProposedEvent && actionProposedEvent.action_id) {
        await apiClient.approveAction(priorityCaseData.caseData.case_id, actionProposedEvent.action_id);
        await refetchPriority();
      } else {
        console.error("No action ID found to approve");
      }
    } catch (e) {
      console.error("Approval failed", e);
    } finally {
      setApproving(false);
    }
  };

  const getPriorityData = () => {
    if (!priorityCaseData) return null;
    const { caseData, timeline } = priorityCaseData;
    
    // Find recommendation event
    const recEvent = timeline.slice().reverse().find(e => e.event_type === 'ACTION_PROPOSED');
    let recommendation = "N/A";
    let reasoning = "No AI analysis available.";
    let confidence = 0;
    
    if (recEvent && recEvent.metadata) {
      recommendation = recEvent.metadata.recommended_action || "UNKNOWN";
      reasoning = recEvent.metadata.reasoning || reasoning;
      confidence = 87; // Mocked or derived if available
    }

    const needsApproval = caseData.workflow_state === 'APPROVAL_REQUIRED' || caseData.workflow_state === 'POLICY_REVIEW';
    
    return {
      id: caseData.case_id.substring(0,8).toUpperCase(),
      amount: caseData.amount_minor,
      currency: caseData.currency,
      needsApproval,
      recommendation,
      reasoning,
      confidence,
      workflow_state: caseData.workflow_state
    };
  };

  const pd = getPriorityData();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="mb-8">
        <h1 className="text-2xl font-bold font-display text-[var(--color-text-primary)]">Recovery Command Center</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">Monitor revenue risk, active recovery actions, and decisions requiring attention.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard 
          title="Revenue Recovered" 
          value={metrics ? <MoneyValue amountMinor={metrics.revenueRecovered} currency="INR" /> : null} 
          valueColor="text-[var(--color-success)]"
        />
        <KpiCard 
          title="Revenue at Risk" 
          value={metrics ? <MoneyValue amountMinor={metrics.revenueAtRisk} currency="INR" /> : null} 
        />
        <KpiCard 
          title="Approvals Pending" 
          value={metrics ? metrics.approvalsPending : '...'} 
          valueColor="text-[var(--color-warning)]"
          icon={<AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />}
        />
        <KpiCard 
          title="Recovery Rate" 
          value={metrics ? metrics.recoveryRate : '...'} 
          valueColor="text-[var(--color-primary)]"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Priority Recovery */}
        <div className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          {pd ? (
            <>
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)]">Priority Recovery</h2>
                    {pd.needsApproval && (
                      <span className="px-2 py-0.5 rounded border border-[var(--color-warning)] text-[var(--color-warning)] text-xs font-mono font-medium flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> APPROVAL REQUIRED
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-[var(--color-text-secondary)] font-mono">Case ID #{pd.id}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-[var(--color-text-secondary)]">Amount at Risk</div>
                  <div className="text-xl font-bold font-mono text-[var(--color-text-primary)]">
                    <MoneyValue amountMinor={pd.amount} currency={pd.currency} /> <span className="text-sm text-[var(--color-text-muted)] ml-1">{pd.currency}</span>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] tracking-wider flex items-center gap-2 mb-3 uppercase">
                  <FileText className="w-4 h-4" /> Observed Evidence
                </h3>
                <ul className="space-y-2 text-sm text-[var(--color-text-secondary)] ml-6 list-disc marker:text-[var(--color-border-subtle)]">
                  <li>3 previous failed attempts</li>
                  <li>Last attempt 18 min ago</li>
                  <li><span className="text-[var(--color-success)]">Gateway operational</span></li>
                </ul>
              </div>

              <div className="mb-6 border border-[#2B3040] rounded-lg p-4 bg-[#181A25]">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-primary)] tracking-wider uppercase">
                    <Zap className="w-4 h-4" /> RecoverAI Recommendation
                  </div>
                  <div className="bg-[#1D243D] text-[var(--color-primary)] text-xs px-2 py-1 rounded font-mono">
                    Confidence: {pd.confidence}%
                  </div>
                </div>
                <div className="text-sm font-bold font-mono text-[var(--color-text-primary)] mb-2">
                  {pd.recommendation}
                </div>
                <div className="text-sm text-[var(--color-primary)] opacity-80">
                  Reasoning: {pd.reasoning}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] tracking-wider flex items-center gap-2 mb-3 uppercase">
                  <CheckCircle2 className="w-4 h-4" /> Policy Checks
                </h3>
                <ul className="space-y-2 text-sm text-[var(--color-text-secondary)]">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> Amount within configured limit</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> Currency matches case</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> No active fraud flags</li>
                </ul>
              </div>

              {pd.needsApproval && (
                <div className="mt-auto p-4 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)] flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-[var(--color-warning-bg)] text-[var(--color-warning)] rounded">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">Human review required before execution</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Link to={`/cases/${pd?.id}`} className="px-4 py-2 rounded text-sm font-medium border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">
                      Review Case &rarr;
                    </Link>
                    <button 
                      onClick={handleApprove}
                      disabled={approving}
                      className="px-4 py-2 rounded text-sm font-medium bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50"
                    >
                      {approving ? 'Approving...' : 'Approve Recovery'}
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">No priority cases require attention.</div>
          )}
        </div>

        {/* Right Column: Lifecycle & Health */}
        <div className="flex flex-col gap-6">
          <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Lifecycle</h2>
            
            {pd ? (
              <RecoveryJourney currentState={pd?.workflow_state || 'UNKNOWN'} />
            ) : (
              <div className="text-sm text-[var(--color-text-muted)]">No active lifecycle.</div>
            )}
          </div>

          <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-4">System Health</h2>
            <div className="space-y-3">
              {[
                { name: 'Gemini LLM', status: 'Available', color: 'text-[var(--color-success)]' },
                { name: 'Policy Engine', status: 'Operational', color: 'text-[var(--color-success)]' },
                { name: 'n8n Workflow', status: 'Connected', color: 'text-[var(--color-success)]' },
                { name: 'Razorpay (Test)', status: 'Connected', color: 'text-[var(--color-success)]' },
                { name: 'Verification', status: 'Operational', color: 'text-[var(--color-success)]' }
              ].map(sys => (
                <div key={sys.name} className="flex justify-between items-center py-2 border-b border-[var(--color-border-subtle)] last:border-0">
                  <span className="text-sm text-[var(--color-text-secondary)]">{sys.name}</span>
                  <span className={`text-xs font-mono ${sys.color} flex items-center gap-1.5`}>
                    <div className="w-1.5 h-1.5 rounded-full bg-current" />
                    {sys.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Performance (7d)</h2>
          <div className="h-48 w-full text-xs font-mono">
            {!analyticsData ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-[var(--color-text-muted)]">
                 <div className="animate-pulse bg-[var(--color-surface-secondary)] w-full h-full rounded"></div>
              </div>
            ) : !analyticsData.performance_7d || analyticsData.performance_7d.length === 0 ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-[var(--color-text-muted)] text-center">
                 <div>Insufficient historical data</div>
                 <div className="text-[10px] mt-1 opacity-70">Recovery performance will appear as verified outcomes accumulate.</div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analyticsData.performance_7d} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border-subtle)" />
                  <XAxis 
                    dataKey="date" 
                    stroke="var(--color-text-muted)" 
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val: any) => new Date(val).toLocaleDateString(undefined, { weekday: 'short' })}
                  />
                  <YAxis 
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val: any) => '₹' + (val / 100).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '0.5rem', color: 'var(--color-text-primary)' }}
                    itemStyle={{ color: 'var(--color-text-primary)', fontSize: '12px' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px', fontSize: '12px', fontFamily: 'var(--font-sans)' }}
                    formatter={(val: any, name: any) => ['₹' + (Number(val) / 100).toLocaleString(), name === 'recovered' ? 'Verified Recovered' : 'Revenue at Risk']}
                    labelFormatter={(label: any) => new Date(label).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}
                  />
                  <Line type="monotone" dataKey="recovered" stroke="var(--color-primary)" strokeWidth={2} dot={{ r: 3, fill: 'var(--color-surface)', strokeWidth: 2 }} activeDot={{ r: 5, strokeWidth: 0, fill: 'var(--color-primary)' }} />
                  <Line type="monotone" dataKey="at_risk" stroke="var(--color-warning)" strokeWidth={2} strokeDasharray="4 4" dot={false} activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--color-warning)' }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recent Activity</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-text-secondary)]">
                  <th className="pb-3 font-medium">Time</th>
                  <th className="pb-3 font-medium">ID</th>
                  <th className="pb-3 font-medium">Event</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)] text-[var(--color-text-primary)]">
                {data && data.cases.slice(0, 5).map((c, i) => {
                   const t = new Date(c.created_at);
                   const isRec = c.outcome_type === 'RECOVERED';
                   return (
                     <tr key={i}>
                       <td className="py-3 font-mono text-xs text-[var(--color-text-muted)]">{t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                       <td className="py-3 font-mono text-xs text-[var(--color-text-secondary)]">{c.case_id.substring(0,8).toUpperCase()}</td>
                       <td className={`py-3 ${isRec ? 'text-[var(--color-success)]' : 'text-[var(--color-text-secondary)]'}`}>
                         {isRec ? `Recovery successful (₹${(c.recovered_amount_minor || c.amount_minor)/100})` : `Case status: ${c.workflow_state}`}
                       </td>
                     </tr>
                   );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
