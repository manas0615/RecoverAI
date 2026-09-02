import { useState, useMemo, useEffect } from 'react';
import { useCases, useCaseDetails } from '../hooks/useApi';
import type { Case } from '../types/domain';
import { StatusBadge } from '../components/status/StatusBadge';
import { MoneyValue } from '../components/financial/MoneyValue';
import { MetricCard } from '../components/data-display/MetricCard';
import { Filter, CheckSquare, AlertTriangle, Clock, ChevronDown, X, Shield, Lock, Activity, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export function ApprovalQueue() {
  const { data, refetch: refetchCases } = useCases();
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  
  const cases = data?.cases || [];

  const pendingApprovals = useMemo(() => {
    return cases
      .filter((c: Case) => c.workflow_state === 'WAITING_APPROVAL')
      .sort((a: Case, b: Case) => new Date(a.updated_at || a.created_at).getTime() - new Date(b.updated_at || b.created_at).getTime());
  }, [cases]);

  useEffect(() => {
    // Select first pending approval if none selected
    if (pendingApprovals.length > 0 && !selectedCaseId) {
      setSelectedCaseId(pendingApprovals[0].case_id);
    } else if (pendingApprovals.length === 0) {
      setSelectedCaseId(null);
    }
  }, [pendingApprovals, selectedCaseId]);

  const totalAmount = useMemo(() => {
    return pendingApprovals.reduce((acc: number, c: Case) => acc + c.amount_minor, 0);
  }, [pendingApprovals]);

  const oldestPendingMin = useMemo(() => {
    if (pendingApprovals.length === 0) return 0;
    const oldest = new Date(pendingApprovals[0].updated_at || pendingApprovals[0].created_at).getTime();
    return Math.floor((Date.now() - oldest) / 60000);
  }, [pendingApprovals]);

  return (
    <div className="max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col pb-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold font-display text-[var(--color-text-primary)] tracking-tight mb-2">
          Approval Queue
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Review recovery actions that require operator authorization.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard 
          label="APPROVALS PENDING" 
          value={pendingApprovals.length} 
          icon={<CheckSquare className="w-4 h-4 text-[var(--color-warning)]" />} 
          labelColor="text-[var(--color-warning)]"
        />
        <MetricCard 
          label="TOTAL AMOUNT AT RISK" 
          value={<><MoneyValue amountMinor={totalAmount} currency="INR" /><span className="text-sm ml-1 text-[var(--color-text-muted)] font-normal">INR</span></>}
          icon={<AlertTriangle className="w-4 h-4 text-red-400" />} 
          labelColor="text-red-400"
        />
        <MetricCard 
          label="HIGH PRIORITY" 
          value={0}
          icon={<AlertTriangle className="w-4 h-4 text-red-500" />} 
          labelColor="text-[var(--color-text-secondary)]"
        />
        <MetricCard 
          label="OLDEST PENDING" 
          value={`${oldestPendingMin} min`}
          icon={<Clock className="w-4 h-4 text-[var(--color-text-secondary)]" />} 
        />
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-4 mb-6">
        <button className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">
          <Filter className="w-4 h-4" />
          Filter
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">
          Status: Pending <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">
          Risk: All <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
        </button>
        <div className="flex-1"></div>
        <button className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">
          Sort: Oldest <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
        </button>
      </div>

      {/* Main Content Split */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        
        {/* Left Pane: Queue */}
        <div className="flex-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] bg-[var(--color-bg)]">
                  <th className="px-6 py-4 font-medium">CASE</th>
                  <th className="px-6 py-4 font-medium">AMOUNT AT RISK</th>
                  <th className="px-6 py-4 font-medium">FAILURE CODE</th>
                  <th className="px-6 py-4 font-medium">AI RECOMMENDATION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {pendingApprovals.map((c: Case) => {
                  const isSelected = c.case_id === selectedCaseId;
                  return (
                    <tr 
                      key={c.case_id} 
                      onClick={() => setSelectedCaseId(c.case_id)}
                      className={`cursor-pointer transition-colors ${isSelected ? 'bg-[var(--color-surface-secondary)]' : 'hover:bg-[var(--color-surface-secondary)]/50'}`}
                    >
                      <td className="px-6 py-4">
                        <div className="font-mono text-sm text-[var(--color-text-primary)]">
                          RC-{c.case_id.slice(0, 4)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-[var(--color-text-primary)]">
                          <MoneyValue amountMinor={c.amount_minor} currency={c.currency} />
                          <span className="text-xs text-[var(--color-text-muted)] ml-1">{c.currency}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-mono text-[11px] px-2 py-1 bg-[var(--color-bg)] rounded inline-block text-[var(--color-text-primary)] truncate max-w-[200px]" title={c.failure_code || 'UNKNOWN'}>
                          {c.failure_code || 'UNKNOWN'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-mono text-xs font-medium text-[var(--color-primary)] truncate max-w-[200px]">
                          {c.recommendation || 'N/A'}
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {pendingApprovals.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-sm text-[var(--color-text-muted)]">
                      No approvals pending. Recovery actions requiring operator authorization will appear here.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane: Selected Detail */}
        <div className="w-full lg:w-[400px] shrink-0 sticky top-6 self-start">
          {selectedCaseId ? (
            <SelectedApprovalPanel 
              caseId={selectedCaseId} 
              onClose={() => setSelectedCaseId(null)} 
              onApproved={refetchCases} 
            />
          ) : (
            <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl flex items-center justify-center p-8 text-center">
              <div className="text-sm text-[var(--color-text-muted)]">
                Select a case from the queue to review and authorize its recovery action.
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

// Inner component to fetch and display the selected case
function SelectedApprovalPanel({ caseId, onClose, onApproved }: { caseId: string, onClose: () => void, onApproved: () => void }) {
  const { data, loading, error, refetch } = useCaseDetails(caseId);
  const [approving, setApproving] = useState(false);

  if (loading) {
    return (
      <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col gap-4">
        <div className="h-8 bg-[var(--color-bg)] rounded animate-pulse w-1/2"></div>
        <div className="h-32 bg-[var(--color-bg)] rounded animate-pulse mt-4"></div>
        <div className="h-32 bg-[var(--color-bg)] rounded animate-pulse"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
        <div className="text-sm text-red-400">Unable to load approval details.</div>
      </div>
    );
  }

  const c = data.caseData;
  const shortId = `RC-${c.case_id.slice(0, 4)}`;

  const handleApprove = async () => {
    if (!c.action_id || approving) return;
    setApproving(true);
    try {
      await apiClient.approveAction(c.case_id, c.action_id);
      onApproved();
      await refetch();
    } catch (err) {
      console.error(err);
      alert('Failed to approve action');
    } finally {
      setApproving(false);
    }
  };

  const isApproved = c.workflow_state !== 'WAITING_APPROVAL';

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)] flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Lock className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h2 className="font-mono font-bold text-[var(--color-text-primary)] text-lg">{shortId}</h2>
            {isApproved ? (
              <StatusBadge status="AUTHORIZED" />
            ) : (
              <StatusBadge status="APPROVAL_REQUIRED" />
            )}
          </div>
          <div className="grid grid-cols-[100px_1fr] gap-y-2 text-sm">
            <div className="text-[var(--color-text-secondary)]">Amount at Risk:</div>
            <div className="font-medium text-[var(--color-text-primary)] text-right">
              <MoneyValue amountMinor={c.amount_minor} currency={c.currency} /> {c.currency}
            </div>
            <div className="text-[var(--color-text-secondary)]">Failure:</div>
            <div className="font-mono text-xs text-red-400 text-right truncate" title={c.failure_code || 'UNKNOWN'}>
              {c.failure_code || 'UNKNOWN'}
            </div>
          </div>
        </div>
        <button onClick={onClose} className="p-1 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex flex-col">
        {/* Observed Evidence */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">OBSERVED EVIDENCE</h3>
          </div>
          <div className="grid grid-cols-2 gap-y-4 gap-x-4 text-xs">
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Previous Attempts</div>
              <div className="font-medium text-[var(--color-text-primary)]">{c.historical_failure_count || 0}</div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Last Attempt</div>
              <div className="font-medium text-[var(--color-warning)]">
                {c.events && c.events.length > 0 
                  ? new Date(c.events[c.events.length - 1].occurred_at || c.events[c.events.length - 1].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                  : 'Unknown'}
              </div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Gateway Status</div>
              <div className="font-medium text-[var(--color-success)]">Operational</div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Historical Falls</div>
              <div className="font-medium text-[var(--color-text-primary)]">{c.historical_failure_count || 0}</div>
            </div>
          </div>
        </div>

        {/* Gemini Recommendation */}
        <div className="p-4 bg-[var(--color-primary)]/5 border-b border-[var(--color-border-subtle)]">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 flex items-center justify-center text-[var(--color-primary)]">✧</div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-primary)]">{c.provenance || 'AI'} Recommendation</h3>
            </div>
            {c.confidence && (
              <span className="text-[10px] font-bold bg-[var(--color-primary)]/10 text-[var(--color-primary)] px-2 py-0.5 rounded">
                {Math.round(c.confidence * 100)}% EXPECTED RECOVERY PROBABILITY
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-[var(--color-primary)] font-bold mb-3">
            &gt; {c.recommendation || 'N/A'}
          </div>
          <p className="text-xs text-[var(--color-text-primary)] italic leading-relaxed mb-3">
            "{c.reasoning || 'No intelligence reasoning available.'}"
          </p>
          <div className="text-[9px] uppercase tracking-wider text-[var(--color-text-muted)]">
            DISCLAIMER: AI RECOMMENDATION IS SUBJECT TO POLICY VALIDATION AND HUMAN APPROVAL.
          </div>
        </div>

        {/* Policy Validation */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">POLICY VALIDATION</h3>
            </div>
            <span className="text-[10px] font-bold bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30 px-2 py-0.5 rounded uppercase">
              {c.policy_decision === 'APPROVE' || c.policy_decision === 'REQUIRE_APPROVAL' ? 'PASSED' : (c.policy_decision || 'PENDING')}
            </span>
          </div>
          <div className="space-y-3">
            {c.policy_reasons && c.policy_reasons.length > 0 ? (
              c.policy_reasons.map((reason: string, i: number) => (
                <div key={i} className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">{reason}</span>
                </div>
              ))
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Amount within configured limit</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Currency matches case</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">No active fraud flags</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Recovery attempt within policy</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">No conflicting active recovery</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Lifecycle / Authorization */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">LIFECYCLE</h3>
          </div>
          
          {isApproved ? (
            <div className="pl-3 border-l-2 border-[var(--color-success)]">
              <h4 className="text-xs font-bold text-[var(--color-success)] uppercase tracking-wider mb-1">
                ACTION AUTHORIZED
              </h4>
              <p className="text-[11px] text-[var(--color-text-secondary)]">
                The recovery action was approved and has progressed to execution.
              </p>
            </div>
          ) : (
            <div className="pl-3 border-l-2 border-[var(--color-warning)]">
              <div className="flex items-start gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-[var(--color-warning)] shrink-0" />
                <div>
                  <h4 className="text-[11px] font-bold font-display uppercase tracking-wider text-[var(--color-warning)] mb-1">
                    OPERATOR AUTHORIZATION REQUIRED
                  </h4>
                  <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
                    This recovery action requires operator approval before financial execution.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 mt-5">
                <button className="px-4 py-2 text-xs font-medium border border-[var(--color-border-subtle)] rounded hover:bg-[var(--color-surface-secondary)] text-red-400 transition-colors focus:outline-none">
                  <span className="mr-1">⊘</span> REJECT
                </button>
                <button 
                  onClick={handleApprove}
                  disabled={approving || !c.action_id}
                  className="flex-1 px-4 py-2 text-xs font-bold bg-[var(--color-primary)] text-[var(--color-bg)] rounded hover:bg-[var(--color-primary)]/90 transition-colors focus:outline-none disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  {approving ? 'AUTHORIZING...' : 'APPROVE RECOVERY'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}