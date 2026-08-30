import { useMemo } from 'react';
import { ArrowLeft, ArrowDown, Brain, Shield, Zap, AlertTriangle, PlayCircle, CheckCircle, CheckCircle2 } from 'lucide-react';
import type { Case, TimelineEvent } from '../types/domain';
import { MoneyValue } from '../components/financial/MoneyValue';
import { StatusBadge } from '../components/status/StatusBadge';
import { RecoveryJourney } from '../components/financial/RecoveryJourney';
import { Timeline } from '../components/data-display/Timeline';

interface CaseDetailViewProps {
  caseData: Case;
  timeline: TimelineEvent[];
  onBack?: () => void;
  onAnalyze?: () => void;
  isAnalyzing?: boolean;
  analyzeError?: string | null;
}

function sanitizeErrorMessage(error: string | null | undefined): string {
  if (!error) return 'Analysis could not be safely completed.';
  if (
    error.includes('Traceback') || 
    error.includes('File "') || 
    error.includes('line ') || 
    error.includes('ValidationError') || 
    error.includes('Exception:') ||
    error.includes('Internal Server Error') ||
    error.includes('500')
  ) {
    return 'Analysis could not be safely validated. Safe fallback policies applied.';
  }
  return error;
}

type ProvenanceStatus = 'gemini_validated' | 'deterministic_fallback' | 'validation_rejected';

function getProvenanceStatus(metadata: Record<string, any> | undefined): ProvenanceStatus {
  if (!metadata) return 'deterministic_fallback';
  if (metadata.validation_status === 'REJECTED' || metadata.validation_passed === false) {
    return 'validation_rejected';
  }
  if (
    metadata.deterministic_fallback === true || 
    metadata.analysis_source === 'Deterministic Fallback' || 
    metadata.model_version?.toLowerCase().includes('deterministic')
  ) {
    return 'deterministic_fallback';
  }
  return 'gemini_validated';
}

export function CaseDetailView({ caseData, timeline, onBack, onAnalyze, isAnalyzing, analyzeError }: CaseDetailViewProps) {
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

    const provenanceStatus = getProvenanceStatus(aiEvent?.metadata);

    return {
      currentState,
      aiEvent,
      policyEvent,
      execEvent,
      verifyEvent,
      needsApproval: currentState === 'WAITING_APPROVAL' || currentState === 'ESCALATED',
      provenanceStatus,
    };
  }, [caseData, timeline]);

  const { currentState, aiEvent, policyEvent, execEvent, verifyEvent, needsApproval, provenanceStatus } = derivedData;

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

          {/* EVIDENCE SECTION */}
          {caseData.events && caseData.events.length > 0 && (
            <>
              <div className="flex flex-col items-center py-2">
                <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
              </div>
              <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">What Happened? (Evidence)</h2>
                </div>
                <div className="space-y-3">
                  <p className="text-sm text-[var(--color-text-secondary)]">The system detected the following events:</p>
                  <div className="flex flex-col gap-3">
                    {caseData.events.map((ev: any) => (
                      <div key={ev.event_id} className="p-3 bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-mono text-sm font-bold text-[var(--color-text-primary)]">{ev.event_type}</span>
                          <span className="text-xs text-[var(--color-text-muted)]">{new Date(ev.occurred_at).toLocaleString()}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          {ev.amount_minor !== undefined && ev.amount_minor !== null ? (
                            <div>
                              <span className="block text-xs text-[var(--color-text-muted)]">Amount</span>
                              <span className="block font-medium text-[var(--color-text-primary)]">
                                {ev.currency ? (
                                  (ev.amount_minor / 100).toLocaleString(undefined, { style: 'currency', currency: ev.currency })
                                ) : (
                                  (ev.amount_minor / 100).toFixed(2)
                                )}
                              </span>
                            </div>
                          ) : (
                            <div>
                              <span className="block text-xs text-[var(--color-text-muted)]">Event Details</span>
                              <span className="block text-xs text-[var(--color-text-secondary)] italic">
                                {ev.metadata && Object.keys(ev.metadata).length > 0 
                                  ? JSON.stringify(ev.metadata) 
                                  : 'Amount unavailable'}
                              </span>
                            </div>
                          )}
                          {ev.external_reference && (
                            <div>
                              <span className="block text-xs text-[var(--color-text-muted)]">Reference</span>
                              <span className="block font-mono text-xs text-[var(--color-text-secondary)]">{ev.external_reference}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            </>
          )}

        {/* Narrative Pipeline */}
        <div className="flex flex-col items-center py-2">
            <ArrowDown className="w-6 h-6 text-[var(--color-border)]" />
        </div>

          {/* ANALYZE CASE BUTTON */}
          {!aiEvent && !isAnalyzing && onAnalyze && (
            <section className="w-full flex flex-col items-center py-4">
              {analyzeError && (
                <div className="mb-4 p-4 rounded-xl bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/30 text-sm text-[var(--color-text-primary)] text-center max-w-lg shadow-sm animate-in fade-in duration-200">
                  <div className="flex items-center justify-center gap-2 text-[var(--color-warning)] font-bold mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Analysis could not be safely validated</span>
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                    {sanitizeErrorMessage(analyzeError)}
                  </p>
                </div>
              )}
              <button
                onClick={onAnalyze}
                className="px-6 py-3 bg-[var(--color-primary)] text-white rounded-lg font-medium shadow-sm hover:opacity-90 transition-opacity"
              >
                {analyzeError ? 'Try Again' : 'Analyze Case'}
              </button>
            </section>
          )}

        {isAnalyzing && (
          <section className="w-full flex flex-col items-center justify-center p-8 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm space-y-4">
            <div className="flex space-x-2 animate-pulse">
              <div className="w-3 h-3 bg-[var(--color-primary)] rounded-full"></div>
              <div className="w-3 h-3 bg-[var(--color-primary)] rounded-full animation-delay-200"></div>
              <div className="w-3 h-3 bg-[var(--color-primary)] rounded-full animation-delay-400"></div>
            </div>
            <div className="text-sm font-medium text-[var(--color-text-primary)]">Analyzing case...</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Reviewing payment context</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Assessing recovery opportunity</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Generating recommendation</div>
          </section>
        )}

        {/* RECOVERY INTELLIGENCE & ASSESSMENT */}
        <section className="w-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[var(--color-border-subtle)]">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-[var(--color-info)]" />
              <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)] uppercase tracking-wider">
                Recovery Intelligence
              </h2>
            </div>
            {aiEvent && (
              <div>
                {provenanceStatus === 'gemini_validated' && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info)]/30">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[var(--color-info)]" />
                    Source: Gemini (Validated)
                  </span>
                )}
                {provenanceStatus === 'deterministic_fallback' && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                    <Shield className="w-3.5 h-3.5 text-[var(--color-neutral)]" />
                    Source: Deterministic Fallback
                  </span>
                )}
                {provenanceStatus === 'validation_rejected' && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning)]/40">
                    <AlertTriangle className="w-3.5 h-3.5 text-[var(--color-warning)]" />
                    Validation: REJECTED
                  </span>
                )}
              </div>
            )}
          </div>

          {aiEvent ? (
            <div className="space-y-6">
              {provenanceStatus === 'validation_rejected' && (
                <div className="flex items-start gap-3 p-4 bg-[var(--color-warning-bg)] border border-[var(--color-warning)]/30 rounded-xl">
                  <AlertTriangle className="w-5 h-5 text-[var(--color-warning)] shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-[var(--color-warning)]">
                      Analysis could not be safely validated
                    </h4>
                    <p className="text-xs text-[var(--color-warning)]/90 leading-relaxed">
                      The AI assessment was rejected because it failed strict schema or evidence grounding checks.
                      The system automatically defaulted to safe deterministic values. No unverified action was taken.
                    </p>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-secondary)]">
                    AI Qualitative Assessment (Hypothesis & Recommendations)
                  </span>
                  <span className="text-[11px] font-mono text-[var(--color-text-muted)]">
                    Model: {aiEvent.metadata?.model_version || 'Unknown'}
                  </span>
                </div>

                <div className="p-4 bg-[var(--color-info-bg)] rounded-xl border border-[var(--color-info)]/20 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-info)]">
                      Proposed Action
                    </span>
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-white/70 text-[var(--color-info)] border border-[var(--color-info)]/20 font-bold">
                      {aiEvent.metadata?.recommended_action || aiEvent.metadata?.recommendation || aiEvent.metadata?.intervention_type || 'REVIEW_REQUIRED'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
                      Reasoning & Narrative
                    </span>
                    <p className="text-sm text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                      {aiEvent.metadata?.reasoning || aiEvent.metadata?.recommendation_reason || 'No reasoning provided.'}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-[var(--color-surface-secondary)] rounded-xl border border-[var(--color-border-subtle)]">
                    <span className="block text-xs uppercase tracking-wider text-[var(--color-text-muted)] mb-1">
                      Predicted Cause Category
                    </span>
                    <span className="text-sm font-bold font-mono text-[var(--color-text-primary)]">
                      {aiEvent.metadata?.cause_category || 'Unknown'}
                    </span>
                  </div>
                  <div className="p-4 bg-[var(--color-surface-secondary)] rounded-xl border border-[var(--color-border-subtle)]">
                    <span className="block text-xs uppercase tracking-wider text-[var(--color-text-muted)] mb-1">
                      AI Confidence Score
                    </span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold font-mono text-[var(--color-text-primary)]">
                        {aiEvent.metadata?.cause_confidence !== undefined || aiEvent.metadata?.confidence !== undefined
                          ? `${((aiEvent.metadata?.cause_confidence ?? aiEvent.metadata?.confidence) * 100).toFixed(0)}%` 
                          : 'Unavailable'}
                      </span>
                      <span className="text-xs text-[var(--color-text-secondary)]">qualitative score</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-[var(--color-border-subtle)] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-secondary)]">
                    Application-Derived Values (Deterministic Financial Calculations)
                  </span>
                  <span className="text-[11px] font-medium text-[var(--color-text-muted)]">
                    Strict Backend Calculation
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-[var(--color-surface-secondary)] rounded-xl border border-[var(--color-border-subtle)] flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs uppercase tracking-wider text-[var(--color-text-muted)]">
                          Expected Recovery Value
                        </span>
                        <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-[var(--color-border)]/50 text-[var(--color-text-secondary)]">
                          Calculated
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-[var(--color-text-primary)] mt-1">
                        {aiEvent.metadata?.expected_recovery_amount !== undefined || aiEvent.metadata?.expected_recovery_value !== undefined ? (
                          <MoneyValue 
                            amountMinor={aiEvent.metadata.expected_recovery_amount ?? aiEvent.metadata.expected_recovery_value} 
                            currency={aiEvent.metadata?.expected_recovery_currency || caseData.currency || 'USD'} 
                          />
                        ) : (
                          <span className="text-sm font-mono text-[var(--color-text-muted)]">Unavailable</span>
                        )}
                      </div>
                    </div>
                    <p className="text-[11px] text-[var(--color-text-secondary)] mt-2 italic">
                      Computed as: Amount at Risk × Recovery Probability
                    </p>
                  </div>

                  <div className="p-4 bg-[var(--color-surface-secondary)] rounded-xl border border-[var(--color-border-subtle)] flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs uppercase tracking-wider text-[var(--color-text-muted)]">
                          Recovery Probability
                        </span>
                        <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-[var(--color-border)]/50 text-[var(--color-text-secondary)]">
                          Empirical
                        </span>
                      </div>
                      <div className="text-2xl font-bold font-mono text-[var(--color-text-primary)] mt-1">
                        {aiEvent.metadata?.recovery_probability !== undefined 
                          ? `${(aiEvent.metadata.recovery_probability * 100).toFixed(0)}%` 
                          : 'Unavailable'}
                      </div>
                    </div>
                    <p className="text-[11px] text-[var(--color-text-secondary)] mt-2">
                      {aiEvent.metadata?.probability_meaning || 'Calculated from historical retry signals and case characteristics.'}
                    </p>
                  </div>
                </div>
                <p className="text-[11px] text-[var(--color-text-muted)] mt-1">
                  * Financial metrics are calculated via deterministic policy rules and arithmetic models; they are never hallucinated by generative language models.
                </p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)] italic">
              No AI recommendation or recovery intelligence recorded for this case.
            </p>
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
          {policyEvent?.metadata?.decision === 'DENY' || policyEvent?.metadata?.decision === 'SUPPRESS' ? (
            <div className="p-4 bg-[var(--color-surface-secondary)] rounded-lg text-[var(--color-text-secondary)] text-sm border border-[var(--color-border)]">
              <strong>EXECUTION BLOCKED</strong> — No downstream API calls or financial mutations occurred.
            </div>
          ) : execEvent ? (
            <div className="space-y-3">
              <div className="p-3 bg-[var(--color-bg)] rounded-lg">
                <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)]">Action Executed</span>
                <p className="mt-1 font-mono text-sm text-[var(--color-text-primary)]">{execEvent.event_type}</p>
              </div>
              {execEvent.metadata && Object.keys(execEvent.metadata).length > 0 && (
                <div className="p-3 bg-[var(--color-bg)] rounded-lg">
                  <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                    {Object.entries(execEvent.metadata).filter(([k]) => typeof execEvent.metadata[k] !== 'object').map(([k, v]) => (
                      <div key={k}>
                        <span className="block text-xs text-[var(--color-text-muted)]">{k}</span>
                        <span className="block font-medium text-[var(--color-text-primary)]">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer text-[var(--color-primary)] font-medium">View Raw Data</summary>
                    <pre className="mt-2 p-2 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded text-[10px] font-mono text-[var(--color-text-secondary)] overflow-x-auto">
                      {JSON.stringify(execEvent.metadata, null, 2)}
                    </pre>
                  </details>
                </div>
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
          {policyEvent?.metadata?.decision === 'DENY' || policyEvent?.metadata?.decision === 'SUPPRESS' ? (
            <p className="text-sm text-[var(--color-text-muted)] italic">Verification Not Applicable.</p>
          ) : verifyEvent ? (
            <div className="space-y-3">
              <StatusBadge status={verifyEvent.new_state || 'UNKNOWN'} />
              {verifyEvent.metadata && Object.keys(verifyEvent.metadata).length > 0 && (
                <div className="p-3 bg-[var(--color-bg)] rounded-lg">
                  <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                    {Object.entries(verifyEvent.metadata).filter(([k]) => typeof verifyEvent.metadata[k] !== 'object').map(([k, v]) => (
                      <div key={k}>
                        <span className="block text-xs text-[var(--color-text-muted)]">{k}</span>
                        <span className="block font-medium text-[var(--color-text-primary)]">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer text-[var(--color-primary)] font-medium">View Raw Data</summary>
                    <pre className="mt-2 p-2 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded text-[10px] font-mono text-[var(--color-text-secondary)] overflow-x-auto">
                      {JSON.stringify(verifyEvent.metadata, null, 2)}
                    </pre>
                  </details>
                </div>
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
