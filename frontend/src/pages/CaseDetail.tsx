import { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Brain, Shield, Zap, AlertTriangle } from 'lucide-react';
import { useCaseDetails } from '../hooks/useCases';
import { ErrorState } from '../components/feedback/ErrorState';
import { LoadingSkeleton } from '../components/feedback/LoadingSkeleton';
import { MoneyValue } from '../components/financial/MoneyValue';
import { StatusBadge } from '../components/status/StatusBadge';
import { RecoveryJourney } from '../components/financial/RecoveryJourney';
import { Timeline } from '../components/data-display/Timeline';

export function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, loading, error, refetch } = useCaseDetails(id);

  const derivedData = useMemo(() => {
    if (!data?.timeline) return null;
    
    // Sort timeline newest first to find latest states
    const events = [...data.timeline].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    // 1. Current workflow state
    const stateChange = events.find(e => e.event_type === 'RECOVERY_STATE_CHANGED');
    const currentState = stateChange?.new_state || data.caseData.status; // fallback to case status

    // 2. AI Recommendation
    const aiEvent = events.find(e => ['LLM_RECOMMENDATION_CREATED', 'INTERVENTION_PROPOSED', 'RISK_ASSESSMENT_CREATED'].includes(e.event_type));
    
    // 3. Policy Decision
    const policyEvent = events.find(e => e.event_type === 'POLICY_DECISION_CREATED');
    
    // 4. Verification/Execution
    const execEvent = events.find(e => e.event_type.startsWith('ACTION_'));
    const verifyEvent = events.find(e => e.event_type.startsWith('VERIFICATION_'));

    return {
      currentState,
      aiEvent,
      policyEvent,
      execEvent,
      verifyEvent,
      needsApproval: currentState === 'WAITING_APPROVAL'
    };
  }, [data]);

  if (error) {
    return <ErrorState message="Case not found or unable to load details." onRetry={refetch} />;
  }

  if (loading || !data || !derivedData) {
    return (
      <div className="space-y-8">
        <LoadingSkeleton className="h-10 w-1/3" />
        <LoadingSkeleton className="h-40 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <LoadingSkeleton className="h-64 w-full" />
          <LoadingSkeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  const { caseData, timeline } = data;
  const { currentState, aiEvent, policyEvent, verifyEvent, needsApproval } = derivedData;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Header */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate('/cases')}
          className="p-2 -ml-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-bold font-mono text-[var(--color-text-primary)] tracking-tight">
          Case {caseData.case_id}
        </h1>
        <StatusBadge status={currentState} className="ml-auto" />
      </div>

      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center p-10 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm">
        <p className="text-sm font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Revenue at Risk</p>
        <MoneyValue 
          amountMinor={caseData.amount_minor} 
          currency={caseData.currency} 
          className="text-4xl md:text-5xl font-display font-bold text-[var(--color-text-primary)] tracking-tight" 
        />
        <div className="w-full mt-10">
          <RecoveryJourney currentState={currentState} />
        </div>
      </div>

      {/* Unknown State Warning */}
      {currentState === 'UNKNOWN' && (
        <div className="flex items-start gap-3 p-4 bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/20 rounded-xl">
          <AlertTriangle className="w-5 h-5 text-[var(--color-warning)] shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-[var(--color-warning)]">External execution state unknown</h4>
            <p className="text-sm text-[var(--color-warning)]/80 mt-1">
              RecoverAI cannot currently confirm whether the recovery action completed.
              Automatic duplicate execution is blocked until state is verified.
            </p>
          </div>
        </div>
      )}

      {/* Needs Approval / Handoff Warning */}
      {needsApproval && (
        <div className="flex flex-col p-6 bg-[var(--color-info-bg)] border border-[var(--color-info)]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-[var(--color-info)]" />
            <h4 className="text-base font-bold text-[var(--color-info)]">Human Approval Required</h4>
          </div>
          
          <p className="text-sm text-[var(--color-info)]/90 mb-4">
            <strong>Workflow Handoff:</strong> Approval and execution orchestration is managed externally via n8n.
          </p>
          
          <div className="bg-white/60 p-4 rounded-lg text-sm text-[var(--color-text-secondary)]">
            <p><strong>Recommendation:</strong> {aiEvent?.metadata?.recommended_action || 'Review required'}</p>
            <p className="mt-2"><strong>Policy Explanation:</strong> {policyEvent?.metadata?.decision_reason || 'Requires manual authorization.'}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Summary & AI */}
        <div className="space-y-8">
          <section className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] mb-4">Case Summary</h2>
            <dl className="grid grid-cols-2 gap-y-4 text-sm">
              <div>
                <dt className="text-[var(--color-text-muted)]">Status</dt>
                <dd className="font-medium text-[var(--color-text-primary)] mt-1">{caseData.status}</dd>
              </div>
              <div>
                <dt className="text-[var(--color-text-muted)]">Created</dt>
                <dd className="font-medium text-[var(--color-text-primary)] mt-1">
                  {new Date(caseData.created_at).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-[var(--color-text-muted)]">Customer ID</dt>
                <dd className="font-mono text-xs text-[var(--color-text-secondary)] mt-1">{caseData.customer_id}</dd>
              </div>
              <div>
                <dt className="text-[var(--color-text-muted)]">Verifications</dt>
                <dd className="font-medium text-[var(--color-text-primary)] mt-1">{caseData.verification_count}</dd>
              </div>
            </dl>
          </section>

          <section className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-[var(--color-info)]" />
              <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)]">AI Recommendation</h2>
            </div>
            
            {aiEvent ? (
              <div className="space-y-4">
                <div className="p-3 bg-[var(--color-info-bg)] rounded-lg">
                  <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-info)]">Proposed Action</span>
                  <p className="mt-1 font-mono text-sm text-[var(--color-text-primary)]">{aiEvent.metadata?.recommended_action || aiEvent.metadata?.intervention_type || 'Unknown'}</p>
                </div>
                {aiEvent.metadata?.reasoning && (
                  <div>
                    <span className="text-xs text-[var(--color-text-muted)]">Reasoning</span>
                    <p className="text-sm text-[var(--color-text-secondary)] mt-1">{aiEvent.metadata.reasoning}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] italic">No AI recommendation event found in timeline.</p>
            )}
          </section>
        </div>

        {/* Right Column: Policy & Verification */}
        <div className="space-y-8">
          <section className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-5 h-5 text-[var(--color-primary)]" />
              <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)]">Policy Decision</h2>
            </div>
            
            {policyEvent ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <StatusBadge status={policyEvent.metadata?.decision || 'UNKNOWN'} />
                </div>
                {policyEvent.metadata?.reasons && Array.isArray(policyEvent.metadata.reasons) && (
                  <div className="flex flex-wrap gap-2">
                    {policyEvent.metadata.reasons.map((r: string) => (
                      <span key={r} className="px-2 py-1 bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] text-[11px] rounded font-mono">
                        {r}
                      </span>
                    ))}
                  </div>
                )}
                {policyEvent.metadata?.decision_reason && (
                  <p className="text-sm text-[var(--color-text-secondary)]">{policyEvent.metadata.decision_reason}</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] italic">No policy decision recorded yet.</p>
            )}
          </section>

          <section className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] mb-4">Verification Outcome</h2>
            {verifyEvent ? (
              <div className="space-y-3">
                <StatusBadge status={verifyEvent.new_state || 'UNKNOWN'} />
                {verifyEvent.metadata && (
                  <pre className="p-3 bg-[var(--color-bg)] rounded-lg text-[10px] font-mono text-[var(--color-text-secondary)] overflow-x-auto">
                    {JSON.stringify(verifyEvent.metadata, null, 2)}
                  </pre>
                )}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-muted)] italic">Verification not completed.</p>
            )}
          </section>
        </div>
      </div>

      {/* Timeline */}
      <section className="pt-8 border-t border-[var(--color-border)]">
        <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Audit Timeline</h2>
        <Timeline events={timeline} />
      </section>
    </div>
  );
}
