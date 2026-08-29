import { useMemo } from 'react';
import { ArrowLeft, ArrowDown, Brain, Shield, Zap, AlertTriangle, PlayCircle, CheckCircle } from 'lucide-react';
import type { Case, TimelineEvent } from '../types/domain';
import { MoneyValue } from '../components/financial/MoneyValue';
import { StatusBadge } from '../components/status/StatusBadge';
import { RecoveryJourney } from '../components/financial/RecoveryJourney';
import { Timeline } from '../components/data-display/Timeline';

interface CaseDetailViewProps {
  caseData: Case;
  timeline: TimelineEvent[];
  onBack?: () => void;
}

export function CaseDetailView({ caseData, timeline, onBack }: CaseDetailViewProps) {
  const derivedData = useMemo(() => {
    // Sort timeline newest first to find latest states
    const events = [...timeline].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    // 1. Current workflow state
    const stateChange = events.find(e => e.event_type === 'RECOVERY_STATE_CHANGED');
    const currentState = stateChange?.new_state || caseData.status;

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
      needsApproval: currentState === 'WAITING_APPROVAL' || currentState === 'ESCALATED'
    };
  }, [caseData, timeline]);

  const { currentState, aiEvent, policyEvent, execEvent, verifyEvent, needsApproval } = derivedData;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Header */}
      <div className="flex items-center gap-4">
        {onBack && (
          <button 
            onClick={onBack}
            className="p-2 -ml-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        )}
        <h1 className="text-2xl font-bold font-mono text-[var(--color-text-primary)] tracking-tight">
          Case {caseData.case_id}
        </h1>
        <StatusBadge status={currentState} className="ml-auto" />
      </div>

      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center p-10 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm">
        <p className="text-sm font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Amount at Risk</p>
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
              Automatic duplicate execution is blocked until state is verified. Reconciliation only.
            </p>
          </div>
        </div>
      )}

      {/* Needs Approval / Escalated Warning */}
      {needsApproval && (
        <div className="flex flex-col p-6 bg-[var(--color-info-bg)] border border-[var(--color-info)]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-[var(--color-info)]" />
            <h4 className="text-base font-bold text-[var(--color-info)]">Human Intervention Required</h4>
          </div>
          
          <p className="text-sm text-[var(--color-info)]/90 mb-4">
            <strong>Workflow Handoff:</strong> Approval, orchestration, and manual escalations are managed externally via n8n.
            The workflow is paused. Human approval does NOT skip backend policy state validation.
          </p>
          
          <div className="bg-white/60 p-4 rounded-lg text-sm text-[var(--color-text-secondary)]">
            <p><strong>Recommendation:</strong> {aiEvent?.metadata?.recommended_action || 'Review required'}</p>
            <p className="mt-2"><strong>Policy Explanation:</strong> {policyEvent?.metadata?.decision_reason || 'Requires manual authorization or review.'}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col items-center max-w-4xl mx-auto space-y-6">
        
        {/* Case Summary */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] mb-4 uppercase tracking-wider">Case Summary (Why did this happen?)</h2>
          <dl className="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-8 text-sm">
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

        {/* Narrative Pipeline */}
        <div className="flex flex-col items-center py-2">
            <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
        </div>

        {/* AI SUGGESTS */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-[var(--color-info)]" />
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">AI Suggests</h2>
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

        <div className="flex flex-col items-center py-2">
            <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
        </div>

        {/* POLICY DECIDES */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-[var(--color-primary)]" />
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">Policy Decides</h2>
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

        <div className="flex flex-col items-center py-2">
            <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
        </div>

        {/* SYSTEM EXECUTES */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <PlayCircle className="w-5 h-5 text-[var(--color-warning)]" />
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">System Executes</h2>
          </div>
          {execEvent ? (
            <div className="space-y-3">
              <div className="p-3 bg-[var(--color-bg)] rounded-lg">
                <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)]">Action Executed</span>
                <p className="mt-1 font-mono text-sm text-[var(--color-text-primary)]">{execEvent.event_type}</p>
              </div>
              {execEvent.metadata && (
                <pre className="p-3 bg-[var(--color-bg)] rounded-lg text-[10px] font-mono text-[var(--color-text-secondary)] overflow-x-auto">
                  {JSON.stringify(execEvent.metadata, null, 2)}
                </pre>
              )}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)] italic">No execution recorded.</p>
          )}
        </section>

        <div className="flex flex-col items-center py-2">
            <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
        </div>

        {/* VERIFICATION PROVES */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-[var(--color-success)]" />
            <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">Verification Proves</h2>
          </div>
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

      {/* Timeline */}
      <section className="pt-12 border-t border-[var(--color-border)]">
        <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Audit Timeline</h2>
        <Timeline events={timeline} />
      </section>
    </div>
  );
}
