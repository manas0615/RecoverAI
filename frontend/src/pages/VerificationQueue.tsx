import { useState, useMemo } from 'react';
import { useCases, useCaseDetails } from '../hooks/useApi';
import { Shield, RefreshCw, X, Filter, CheckCircle, AlertTriangle } from 'lucide-react';
import type { Case } from '../types/domain';

// --- Utility Components ---
function MoneyValue({ amountMinor }: { amountMinor?: number | null, currency?: string | null }) {
  if (amountMinor == null) return <span>N/A</span>;
  const amount = amountMinor / 100;
  return <span>{amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>;
}

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case 'VERIFIED_SUCCESS':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Verified</span>;
    case 'VERIFIED_FAILURE':
    case 'NOT_RECOVERED':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-bg)] text-[var(--color-text-secondary)] border border-[var(--color-border)] flex items-center gap-1"><X className="w-3 h-3" /> Not Recovered</span>;
    case 'UNKNOWN':
    case 'EXECUTION_UNKNOWN':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Unknown</span>;
    case 'VERIFICATION_PENDING':
    default:
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-warning)]/10 text-[var(--color-warning)] border border-[var(--color-warning)]/30 flex items-center gap-1"><RefreshCw className="w-3 h-3 animate-spin" /> Pending</span>;
  }
}

function VerificationResultBadge({ result }: { result: string }) {
  switch (result) {
    case 'SUCCESS':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30">SUCCESS</span>;
    case 'MISMATCH':
    case 'FAILURE':
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30">MISMATCH</span>;
    case 'PENDING':
    default:
      return <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-warning)]/10 text-[var(--color-warning)] border border-[var(--color-warning)]/30">PENDING</span>;
  }
}

// --- Main VerificationQueue Component ---
export function VerificationQueue() {
  const { data, loading, refetch } = useCases();
  const cases = data?.cases || [];
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const verificationCases = useMemo(() => {
    return cases.filter((c: Case) => ['VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE', 'EXECUTION_UNKNOWN'].includes(c.action_status || ''));
  }, [cases]);

  // Set default selection when data loads
  useMemo(() => {
    if (!selectedCaseId && verificationCases.length > 0) {
      setSelectedCaseId(verificationCases[0].case_id);
    }
  }, [verificationCases, selectedCaseId]);

  const stats = useMemo(() => {
    return {
      pending: verificationCases.filter(c => c.action_status === 'VERIFICATION_PENDING').length,
      verified: verificationCases.filter(c => c.action_status === 'VERIFIED_SUCCESS').length,
      notRecovered: verificationCases.filter(c => c.action_status === 'VERIFIED_FAILURE').length,
      issues: verificationCases.filter(c => c.action_status === 'EXECUTION_UNKNOWN').length
    };
  }, [verificationCases]);

  return (
    <div className="max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col pb-8">
      {/* Page Header */}
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-display font-bold text-[var(--color-text-primary)] mb-1">Verification</h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Confirm provider outcomes before recording a recovery.
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors">
            <Filter className="w-3.5 h-3.5" /> Filter
          </button>
          <div className="relative">
            <input 
              type="text"
              placeholder="Search case or provider ref"
              className="bg-[var(--color-bg)] border border-[var(--color-border)] rounded px-3 py-1.5 text-xs w-48 focus:outline-none focus:border-[var(--color-primary)] transition-colors text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)]"
            />
          </div>
          <button onClick={() => refetch()} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Data
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">VERIFICATION PENDING</h3>
            <RefreshCw className="w-4 h-4 text-[var(--color-warning)]" />
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.pending}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-success)]">VERIFIED RECOVERIES</h3>
            <CheckCircle className="w-4 h-4 text-[var(--color-success)]" />
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-success)]">{stats.verified}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">NOT RECOVERED</h3>
            <X className="w-4 h-4 text-[var(--color-text-muted)]" />
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.notRecovered}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">VERIFICATION ISSUES</h3>
            <AlertTriangle className="w-4 h-4 text-[var(--color-text-muted)]" />
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.issues}</div>
        </div>
      </div>

      {/* Main Content Split */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        
        {/* Left Pane: Queue */}
        <div className="flex-1 lg:w-[60%] shrink-0 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-[var(--color-border)] flex justify-between items-center bg-[var(--color-bg)]">
            <h2 className="font-bold text-sm text-[var(--color-text-primary)]">Verification Queue</h2>
            <span className="text-xs text-[var(--color-text-muted)]">Showing {verificationCases.length} records</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                  <th className="px-4 py-3 font-medium">CASE ID</th>
                  <th className="px-4 py-3 font-medium">ACTION</th>
                  <th className="px-4 py-3 font-medium text-right">AMOUNT</th>
                  <th className="px-4 py-3 font-medium">PROVIDER</th>
                  <th className="px-4 py-3 font-medium">RESULT</th>
                  <th className="px-4 py-3 font-medium">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                      Loading verification data...
                    </td>
                  </tr>
                ) : verificationCases.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      No provider outcomes require verification.
                    </td>
                  </tr>
                ) : (
                  verificationCases.map((c: Case) => {
                    const isSelected = selectedCaseId === c.case_id;
                    const shortId = `RC-${c.case_id.slice(0, 4)}`;
                    const providerResult = c.action_status === 'VERIFIED_SUCCESS' ? 'SUCCESS' : c.action_status === 'EXECUTION_UNKNOWN' ? 'MISMATCH' : 'PENDING';

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
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="font-mono text-sm font-medium text-[var(--color-primary)]">{shortId}</div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="text-xs font-mono text-[var(--color-text-primary)] truncate max-w-[120px]">
                            {c.action_type === 'CREATE_PAYMENT_LINK' ? 'Capture' : c.action_type || 'UNKNOWN'}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-right">
                          <div className="font-mono text-xs text-[var(--color-text-primary)]">
                            <MoneyValue amountMinor={c.amount_minor} />
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="text-xs text-[var(--color-text-secondary)] truncate max-w-[120px]">
                            {c.provider || 'N/A'}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <VerificationResultBadge result={providerResult} />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <StatusBadge status={c.action_status || ''} />
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
        <div className="flex-1 lg:w-[40%] shrink-0 sticky top-6 self-start">
          {selectedCaseId ? (
            <SelectedVerificationPanel 
              caseId={selectedCaseId} 
            />
          ) : (
            <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl flex items-center justify-center p-8 text-center">
              <div className="text-sm text-[var(--color-text-muted)]">
                Select a verification record to review.
              </div>
            </div>
          )}
        </div>

      </div>
      
      {/* Verification Boundary Banner */}
      <div className="mt-8 flex items-center justify-center gap-2 p-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-muted)] text-xs">
        <Shield className="w-3.5 h-3.5" />
        <strong>Verification Boundary:</strong> Recovery outcomes are recorded only after provider evidence is independently verified.
      </div>
    </div>
  );
}

// --- Selected Verification Panel ---
function SelectedVerificationPanel({ caseId }: { caseId: string }) {
  const { data, loading, error } = useCaseDetails(caseId);

  if (loading) {
    return (
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col gap-4 min-h-[500px]">
        <div className="h-8 bg-[var(--color-bg)] rounded animate-pulse w-1/2"></div>
        <div className="h-32 bg-[var(--color-bg)] rounded animate-pulse mt-4"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
        <div className="text-sm text-red-400">Unable to load verification data.</div>
      </div>
    );
  }

  const c = data.caseData;
  const shortId = `RC-${c.case_id.slice(0, 4)}`;

  const isVerified = c.action_status === 'VERIFIED_SUCCESS';
  const isFailed = c.action_status === 'VERIFIED_FAILURE' || c.action_status === 'EXECUTION_UNKNOWN';
  const isPending = !isVerified && !isFailed;
  
  const expectedAmount = c.amount_minor;
  const expectedCurrency = c.currency;
  const expectedRef = c.external_reference;
  
  const observedAmount = c.observed_amount_minor;
  const observedCurrency = c.observed_currency;
  const observedRef = c.observed_reference || (isPending ? 'Pending' : c.external_reference);
  const observedEvent = c.observed_event_type || 'PAYMENT_CAPTURED';

  const amountMatch = expectedAmount === observedAmount && observedAmount != null;
  const currencyMatch = expectedCurrency === observedCurrency && observedCurrency != null;
  const refMatch = expectedRef === observedRef && observedRef != null;

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col overflow-hidden text-sm">
      
      {/* Header */}
      <div className="p-4 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)]">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <h2 className="font-mono font-bold text-[var(--color-text-primary)] text-lg">{shortId}</h2>
            <StatusBadge status={c.action_status || ''} />
          </div>
        </div>
        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Verification Details</div>
      </div>

      {/* Execution Record */}
      <div className="p-4 border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-3">EXECUTION RECORD</h3>
        <div className="grid grid-cols-[80px_1fr] gap-y-2 text-xs">
          <div className="text-[var(--color-text-secondary)]">Auth:</div>
          <div className="text-right text-[var(--color-text-primary)] truncate">Approved</div>
          <div className="text-[var(--color-text-secondary)]">Provider:</div>
          <div className="text-right text-[var(--color-text-primary)] truncate">{c.provider || 'N/A'}</div>
          <div className="text-[var(--color-text-secondary)]">Ref:</div>
          <div className="text-right font-mono text-[var(--color-text-primary)] truncate">{c.external_reference || 'N/A'}</div>
        </div>
      </div>

      {/* Provider Outcome */}
      <div className="p-4 border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-3">PROVIDER OUTCOME</h3>
        <div className="grid grid-cols-[80px_1fr] gap-y-2 text-xs">
          <div className="text-[var(--color-text-secondary)]">Event:</div>
          <div className="text-right font-mono text-[var(--color-text-primary)] truncate">{isPending ? 'PENDING' : observedEvent}</div>
          <div className="text-[var(--color-text-secondary)]">Status:</div>
          <div className="text-right text-[var(--color-text-primary)] truncate">
            {isVerified ? <span className="text-[var(--color-success)] font-medium">SUCCESS</span> : 
             isFailed ? <span className="text-red-400 font-medium">MISMATCH</span> : 
             <span className="text-[var(--color-warning)] font-medium">PENDING</span>}
          </div>
        </div>
      </div>

      {/* Verification Engine */}
      <div className="p-4 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)] relative">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-1.5">
            <Shield className={`w-4 h-4 ${isVerified ? 'text-[var(--color-success)]' : isFailed ? 'text-red-400' : 'text-[var(--color-text-muted)]'}`} />
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)]">VERIFICATIONENGINE (P09)</h3>
          </div>
          {isVerified && <span className="text-[10px] font-bold text-[var(--color-success)] tracking-wider">100% MATCH</span>}
        </div>
        
        <div className="space-y-2 text-xs mb-4">
          <div className="flex items-center gap-2">
            {refMatch ? <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)]" /> : isPending ? <RefreshCw className="w-3.5 h-3.5 text-[var(--color-warning)] animate-spin" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span className={refMatch ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}>Provider Reference Match</span>
          </div>
          <div className="flex items-center gap-2">
            {isVerified ? <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)]" /> : isPending ? <RefreshCw className="w-3.5 h-3.5 text-[var(--color-warning)] animate-spin" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span className={isVerified ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}>Status 'SUCCESS' Confirmed</span>
          </div>
          <div className="flex items-center gap-2">
            {amountMatch ? <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)]" /> : isPending ? <RefreshCw className="w-3.5 h-3.5 text-[var(--color-warning)] animate-spin" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span className={amountMatch ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}>Amount Exact Match ({(expectedAmount||0)/100})</span>
          </div>
          <div className="flex items-center gap-2">
            {currencyMatch ? <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)]" /> : isPending ? <RefreshCw className="w-3.5 h-3.5 text-[var(--color-warning)] animate-spin" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span className={currencyMatch ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}>Currency Match ({expectedCurrency})</span>
          </div>
          <div className="flex items-center gap-2">
            {isVerified ? <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)]" /> : isPending ? <RefreshCw className="w-3.5 h-3.5 text-[var(--color-warning)] animate-spin" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span className={isVerified ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}>Event Type Validated</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-xs border-t border-[var(--color-border-subtle)] pt-3">
          <span className="text-[var(--color-text-secondary)]">Engine Result:</span>
          <span className={`font-bold uppercase ${isVerified ? 'text-[var(--color-success)]' : isFailed ? 'text-red-400' : 'text-[var(--color-warning)]'}`}>
            {isVerified ? 'VERIFIED RECOVERY' : isFailed ? 'UNKNOWN / MISMATCH' : 'VERIFICATION PENDING'}
          </span>
        </div>
      </div>

      {/* Evidence Comparison */}
      <div className="p-4 border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-3">EVIDENCE COMPARISON</h3>
        
        <div className="grid grid-cols-2 text-[10px] uppercase font-bold tracking-wider text-[var(--color-text-muted)] mb-2">
          <div className="text-center">EXPECTED (DB)</div>
          <div className="text-center">OBSERVED (API)</div>
        </div>

        <div className="grid grid-cols-2 gap-x-4 text-xs font-mono">
          <div className="space-y-1">
            <div className="text-[var(--color-text-primary)]"><MoneyValue amountMinor={expectedAmount} /></div>
            <div className="text-[var(--color-text-primary)]">{expectedCurrency}</div>
            <div className="text-[var(--color-text-primary)] truncate">{expectedRef || 'N/A'}</div>
          </div>
          <div className="space-y-1 pl-4 border-l border-[var(--color-border-subtle)]">
            <div className={amountMatch ? 'text-[var(--color-success)]' : 'text-red-400'}>
              {observedAmount != null ? <MoneyValue amountMinor={observedAmount} /> : 'Pending'}
            </div>
            <div className={currencyMatch ? 'text-[var(--color-success)]' : 'text-red-400'}>
              {observedCurrency || 'Pending'}
            </div>
            <div className={refMatch ? 'text-[var(--color-success)]' : 'text-red-400 truncate'}>
              {observedRef || 'Pending'}
            </div>
          </div>
        </div>
      </div>

      {/* Lifecycle */}
      <div className="p-4 border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-4">LIFECYCLE</h3>
        
        <div className="space-y-3 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-[var(--color-border-subtle)]">
          <div className="flex items-start gap-3 relative z-10">
            <div className="w-4 h-4 rounded-full bg-[var(--color-success)] flex items-center justify-center shrink-0 mt-0.5"><div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div></div>
            <div className="flex flex-col">
              <span className="text-xs text-[var(--color-text-primary)] font-medium">Case Initiated</span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)]">{new Date(c.created_at).toISOString().split('T')[1].slice(0,8)} UTC</span>
            </div>
          </div>
          <div className="flex items-start gap-3 relative z-10">
            <div className="w-4 h-4 rounded-full bg-[var(--color-success)] flex items-center justify-center shrink-0 mt-0.5"><div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div></div>
            <div className="flex flex-col">
              <span className="text-xs text-[var(--color-text-primary)] font-medium">Execution Approved</span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)]">{c.action_requested_at ? new Date(c.action_requested_at).toISOString().split('T')[1].slice(0,8) + ' UTC' : 'Pending'}</span>
            </div>
          </div>
          <div className="flex items-start gap-3 relative z-10">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${c.action_executed_at || isVerified ? 'bg-[var(--color-success)]' : 'bg-[var(--color-border)]'}`}><div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div></div>
            <div className="flex flex-col">
              <span className={`text-xs font-medium ${c.action_executed_at || isVerified ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'}`}>Provider Captured</span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)]">{c.action_executed_at ? new Date(c.action_executed_at).toISOString().split('T')[1].slice(0,8) + ' UTC' : isVerified ? 'Recorded' : 'Pending'}</span>
            </div>
          </div>
          <div className="flex items-start gap-3 relative z-10">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${isVerified ? 'bg-[var(--color-success)]' : isFailed ? 'bg-red-500' : 'bg-[var(--color-border)]'}`}><div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div></div>
            <div className="flex flex-col">
              <span className={`text-xs font-medium ${isVerified ? 'text-[var(--color-success)]' : isFailed ? 'text-red-400' : 'text-[var(--color-text-muted)]'}`}>Recovery Outcome</span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)]">
                {isVerified ? 'Verified • ' + (c.verification_checked_at ? new Date(c.verification_checked_at).toISOString().split('T')[1].slice(0,8) + ' UTC' : 'Recorded') : 
                 isFailed ? 'Unknown / Not Recovered' : 'Pending'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 bg-[var(--color-bg)] flex gap-3">
        <button className="flex-1 px-4 py-2 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors focus:outline-none">
          View Raw API
        </button>
        <button 
          disabled={!isVerified}
          className={`flex-1 px-4 py-2 text-xs font-medium rounded transition-colors focus:outline-none disabled:opacity-50 ${
            isVerified 
              ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] border border-transparent' 
              : 'bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-muted)]'
          }`}
        >
          Record Ledger
        </button>
      </div>
      
    </div>
  );
}
