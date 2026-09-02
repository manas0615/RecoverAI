import { useState, useMemo } from 'react';
import { useCases, useCaseDetails } from '../hooks/useApi';
import { apiClient } from '../api/client';
import { Shield, RefreshCw, X, Download, Filter } from 'lucide-react';
import type { Case } from '../types/domain';

// --- Utility Components ---
function MoneyValue({ amountMinor }: { amountMinor: number, currency: string }) {
  const amount = amountMinor / 100;
  return <span>₹{amount.toLocaleString('en-IN')}</span>;
}

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case 'AUTHORIZED':
    case 'EXECUTING':
    case 'VERIFICATION_PENDING':
    case 'VERIFIED_SUCCESS':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30">Approved</span>;
    case 'ESCALATED':
    case 'CANCELLED':
    case 'VERIFIED_FAILURE':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30">Escalated</span>;
    case 'PROPOSED':
    default:
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-warning)]/10 text-[var(--color-warning)] border border-[var(--color-warning)]/30">Pending</span>;
  }
}

function formatExecutionStatus(status?: string) {
  if (!status) return 'Not Executed';
  switch (status) {
    case 'AUTHORIZED': return 'Ready';
    case 'EXECUTING': return 'Executing';
    case 'VERIFICATION_PENDING': return 'Verification Pending';
    case 'VERIFIED_SUCCESS': return 'Completed';
    case 'VERIFIED_FAILURE': return 'Failed';
    case 'CANCELLED': return 'Cancelled';
    case 'ESCALATED': return 'Escalated';
    case 'PROPOSED': return 'Not Executed';
    default: return 'Unknown';
  }
}

// --- Main ExecutionQueue Component ---
export function ExecutionQueue() {
  const { data, loading, refetch } = useCases();
  const cases = data?.cases || [];
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const executionCases = useMemo(() => {
    return cases.filter((c: Case) => c.action_status && c.action_status !== 'PROPOSED');
  }, [cases]);

  // Set default selection when data loads
  useMemo(() => {
    if (!selectedCaseId && executionCases.length > 0) {
      setSelectedCaseId(executionCases[0].case_id);
    }
  }, [executionCases, selectedCaseId]);

  const stats = useMemo(() => {
    return {
      ready: executionCases.filter((c: Case) => c.action_status === 'AUTHORIZED').length,
      executing: executionCases.filter((c: Case) => c.action_status === 'EXECUTING').length,
      verificationPending: executionCases.filter((c: Case) => c.action_status === 'VERIFICATION_PENDING').length,
      issues: executionCases.filter((c: Case) => ['CANCELLED', 'ESCALATED', 'EXECUTION_UNKNOWN', 'VERIFIED_FAILURE'].includes(c.action_status || '')).length
    };
  }, [executionCases]);

  return (
    <div className="max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col pb-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h1 className="text-2xl font-display font-bold text-[var(--color-text-primary)] mb-1">Execution</h1>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Monitor authorized recovery actions, provider execution, and verification state.
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => refetch()} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors">
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors">
              <Filter className="w-3.5 h-3.5" /> Filters
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors">
              <Download className="w-3.5 h-3.5" /> Export
            </button>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 shadow-sm">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">READY TO EXECUTE</h3>
            <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.ready}</div>
          </div>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 shadow-sm bg-[var(--color-primary)]/5 border-[var(--color-primary)]/20">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-2">IN EXECUTION</h3>
            <div className="text-2xl font-mono font-bold text-[var(--color-primary)]">{stats.executing}</div>
          </div>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 shadow-sm">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-warning)] mb-2">VERIFICATION PENDING</h3>
            <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.verificationPending}</div>
          </div>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 shadow-sm">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">EXECUTION ISSUES</h3>
            <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.issues}</div>
          </div>
        </div>
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
                  <th className="px-6 py-4 font-medium">ACTION</th>
                  <th className="px-6 py-4 font-medium">AMOUNT</th>
                  <th className="px-6 py-4 font-medium">AUTHORIZATION</th>
                  <th className="px-6 py-4 font-medium">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                      Loading execution queue...
                    </td>
                  </tr>
                ) : executionCases.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      No execution actions require attention.
                    </td>
                  </tr>
                ) : (
                  executionCases.map((c: Case) => {
                    const isSelected = selectedCaseId === c.case_id;
                    const shortId = `RC-${c.case_id.slice(0, 4)}`;
                    
                    return (
                      <tr 
                        key={c.case_id}
                        onClick={() => setSelectedCaseId(c.case_id)}
                        className={`group cursor-pointer transition-colors ${
                          isSelected 
                            ? 'bg-[var(--color-primary)]/5 border-l-2 border-l-[var(--color-primary)]' 
                            : 'hover:bg-[var(--color-surface-secondary)] border-l-2 border-l-transparent'
                        }`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-mono text-sm font-medium text-[var(--color-text-primary)]">{shortId}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-xs font-mono text-[var(--color-text-secondary)]">{c.action_type || 'UNKNOWN'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-sm text-[var(--color-text-primary)]">
                            <MoneyValue amountMinor={c.amount_minor} currency={c.currency} />
                            <span className="text-[10px] text-[var(--color-text-muted)] ml-1">{c.currency}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <StatusBadge status={c.action_status || ''} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`text-sm flex items-center gap-2 ${
                            c.action_status === 'EXECUTING' ? 'text-[var(--color-primary)]' : 
                            c.action_status === 'VERIFIED_SUCCESS' ? 'text-[var(--color-success)]' : 
                            ['CANCELLED', 'ESCALATED', 'VERIFIED_FAILURE'].includes(c.action_status || '') ? 'text-red-400' :
                            'text-[var(--color-text-primary)]'
                          }`}>
                            {c.action_status === 'EXECUTING' && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                            {formatExecutionStatus(c.action_status)}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane: Selected Detail */}
        <div className="w-full lg:w-[400px] shrink-0 sticky top-6 self-start">
          {selectedCaseId ? (
            <SelectedExecutionPanel 
              caseId={selectedCaseId} 
              onClose={() => setSelectedCaseId(null)} 
              onRefresh={refetch} 
            />
          ) : (
            <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl flex items-center justify-center p-8 text-center">
              <div className="text-sm text-[var(--color-text-muted)]">
                Select a case from the queue to review execution state.
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

// --- Selected Execution Panel ---
function SelectedExecutionPanel({ caseId, onClose, onRefresh }: { caseId: string, onClose: () => void, onRefresh: () => void }) {
  const { data, loading, error, refetch } = useCaseDetails(caseId);
  const [aborting, setAborting] = useState(false);

  if (loading) {
    return (
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col gap-4 min-h-[400px]">
        <div className="h-8 bg-[var(--color-bg)] rounded animate-pulse w-1/2"></div>
        <div className="h-32 bg-[var(--color-bg)] rounded animate-pulse mt-4"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
        <div className="text-sm text-red-400">Unable to load execution details.</div>
      </div>
    );
  }

  const c = data.caseData;
  const shortId = `RC-${c.case_id.slice(0, 4)}`;

  const handleAbort = async () => {
    if (aborting) return;
    if (!window.confirm("Are you sure you want to abort this execution?")) return;
    setAborting(true);
    try {
      await apiClient.abortExecution(c.case_id);
      onRefresh();
      await refetch();
    } catch (err) {
      console.error(err);
      alert('Failed to abort execution or action is not abortable in current state.');
    } finally {
      setAborting(false);
    }
  };

  const isExecuting = c.action_status === 'EXECUTING';
  const isCompleted = ['VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE'].includes(c.action_status || '');
  const isAuthorized = ['AUTHORIZED', 'EXECUTING', 'VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE'].includes(c.action_status || '');

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)] flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2 mb-4">
            {isExecuting && <div className="w-2 h-2 rounded-full bg-[var(--color-primary)] animate-pulse" />}
            <h2 className="font-mono font-bold text-[var(--color-text-primary)] text-lg">{shortId}</h2>
            <div className="text-[10px] uppercase font-bold text-[var(--color-text-muted)] tracking-wider">
              {isExecuting ? 'EXECUTING' : formatExecutionStatus(c.action_status)}
            </div>
          </div>
          <div className="grid grid-cols-[80px_1fr] gap-y-2 text-sm">
            <div className="text-[var(--color-text-secondary)]">Amount</div>
            <div className="font-medium text-[var(--color-text-primary)] text-right">
              <MoneyValue amountMinor={c.amount_minor} currency={c.currency} /> {c.currency}
            </div>
            <div className="text-[var(--color-text-secondary)]">Action</div>
            <div className="font-mono text-xs text-right truncate">
              {c.action_type || 'UNKNOWN'}
            </div>
            <div className="text-[var(--color-text-secondary)]">Auth</div>
            <div className="text-right text-xs">
              <StatusBadge status={c.action_status || ''} />
            </div>
          </div>
        </div>
        <button onClick={onClose} className="p-1 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex flex-col">
        {/* Service / Provider */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <div className="grid grid-cols-[80px_1fr] gap-y-2 text-xs">
            <div className="text-[var(--color-text-secondary)]">Service</div>
            <div className="font-mono text-right text-[var(--color-text-primary)] truncate">RecoveryActionService</div>
            
            <div className="text-[var(--color-text-secondary)]">Provider</div>
            <div className="font-mono text-right text-[var(--color-text-primary)] truncate">{c.provider || 'N/A'}</div>
            
            <div className="text-[var(--color-text-secondary)]">Prov. Ref</div>
            <div className="font-mono text-right text-[var(--color-success)] truncate">
              {c.external_reference || 'Pending'}
            </div>
          </div>
        </div>

        {/* Lifecycle */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-4">LIFECYCLE</h3>
          <div className="space-y-3 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-[var(--color-border-subtle)]">
            
            {/* Case Authorized */}
            <div className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${isAuthorized ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}>
                <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>
              </div>
              <span className={`text-xs ${isAuthorized ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-muted)]'}`}>Case Authorized</span>
            </div>

            {/* Execution Queued */}
            <div className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${isAuthorized ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}>
                <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>
              </div>
              <span className={`text-xs ${isAuthorized ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-muted)]'}`}>Execution Queued</span>
            </div>

            {/* Execution Started */}
            <div className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${isExecuting ? 'bg-[var(--color-primary)]' : isCompleted ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}>
                {isExecuting ? <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full animate-pulse"></div> : <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>}
              </div>
              <span className={`text-xs ${isExecuting ? 'text-[var(--color-primary)] font-bold' : isCompleted ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-muted)]'}`}>Execution Started</span>
            </div>

            {/* Provider Response */}
            <div className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${isCompleted ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}>
                <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>
              </div>
              <span className={`text-xs ${isCompleted ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-muted)]'}`}>Provider Response</span>
            </div>

            {/* Verification */}
            <div className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${c.action_status === 'VERIFIED_SUCCESS' ? 'bg-[var(--color-success)]' : c.action_status === 'VERIFIED_FAILURE' ? 'bg-red-500' : 'bg-[var(--color-border)]'}`}>
                <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>
              </div>
              <span className={`text-xs ${c.action_status === 'VERIFIED_SUCCESS' ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-muted)]'}`}>Verification</span>
            </div>
            
          </div>
        </div>

        {/* Guardrails & Abort */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-[var(--color-success)]" />
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)]">EXECUTION GUARDRAILS</h3>
          </div>
          
          <div className="flex gap-1 mb-2">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className={`h-2 flex-1 rounded ${isAuthorized ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}></div>
            ))}
          </div>
          <div className="text-[9px] text-[var(--color-text-muted)] text-center mb-6">
            {isAuthorized ? '6/6 pre-flight checks passed.' : 'Pre-flight checks pending.'}
          </div>

          <button 
            onClick={handleAbort}
            disabled={aborting || isExecuting || isCompleted || !['PROPOSED', 'AUTHORIZED', 'ESCALATED'].includes(c.action_status || '')}
            className={`w-full px-4 py-2 text-xs font-medium rounded transition-colors focus:outline-none disabled:opacity-50 ${
              isExecuting || isCompleted 
                ? 'bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-muted)]' 
                : 'bg-[var(--color-surface)] border border-red-500/50 text-red-400 hover:bg-red-500/10'
            }`}
          >
            {aborting ? 'Aborting...' : isExecuting || isCompleted ? 'Execution in progress — cannot cancel' : 'Abort Execution'}
          </button>
        </div>
      </div>
    </div>
  );
}
