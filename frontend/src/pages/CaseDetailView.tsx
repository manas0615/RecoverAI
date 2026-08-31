import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Case, TimelineEvent } from '../types/domain';
import { StatusBadge } from '../components/status/StatusBadge';
import { MoneyValue } from '../components/financial/MoneyValue';
import { RecoveryJourney } from '../components/financial/RecoveryJourney';
import { CheckCircle, AlertTriangle, ChevronRight } from 'lucide-react';
import { apiClient } from '../api/client';

interface CaseDetailViewProps {
  caseData: Case;
  timeline: TimelineEvent[];
  onBack?: () => void;
  onAnalyze?: () => void;
  isAnalyzing?: boolean;
  analyzeError?: string | null;
}

export function CaseDetailView({ caseData, timeline }: CaseDetailViewProps) {
  const [approving, setApproving] = useState(false);

  const handleApprove = async () => {
    if (!caseData.action_id || approving) return;
    setApproving(true);
    try {
      await apiClient.approveAction(caseData.case_id, caseData.action_id);
      // Reload page to get new state
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert('Failed to approve action');
    } finally {
      setApproving(false);
    }
  };

  const shortId = `RC-${caseData.case_id.slice(0, 4)}`;
  const needsApproval = caseData.workflow_state === 'WAITING_APPROVAL';
  const derivedStatus = needsApproval ? 'APPROVAL_REQUIRED' : 
                        (caseData.outcome_type === 'RECOVERED' ? 'RECOVERED' : 
                        (caseData.workflow_state === 'EXECUTING' ? 'EXECUTING' : 
                        (caseData.workflow_state === 'ESCALATED' ? 'ESCALATED' : caseData.status)));

  const createdDate = new Date(caseData.created_at);
  const updatedDate = caseData.updated_at ? new Date(caseData.updated_at) : createdDate;

  return (
    <div className="max-w-[1440px] mx-auto animate-in fade-in duration-300">
      {/* Breadcrumb */}
      <div className="flex items-center text-xs text-[var(--color-text-secondary)] mb-6 font-medium">
        <Link to="/cases" className="hover:text-[var(--color-text-primary)] transition-colors">Recovery Cases</Link>
        <ChevronRight className="w-3 h-3 mx-2 text-[var(--color-border)]" />
        <span className="font-mono text-[var(--color-text-primary)]">{shortId}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold font-display text-[var(--color-text-primary)] tracking-tight">
              Recovery Case
            </h1>
            <StatusBadge status={derivedStatus} />
          </div>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {needsApproval 
              ? 'Manual operator approval required for proposed recovery action.' 
              : 'Review case details, evidence, and lifecycle.'}
          </p>
        </div>
        
        <div className="text-right">
          <div className="text-sm text-[var(--color-text-secondary)] mb-1">Amount at Risk</div>
          <div className="text-2xl font-bold font-display text-[var(--color-text-primary)]">
            <MoneyValue amountMinor={caseData.amount_minor} currency={caseData.currency} />
            <span className="text-sm text-[var(--color-text-muted)] ml-1 font-normal">{caseData.currency}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT / MAIN COLUMN */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* Case Summary */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-bold font-display text-[var(--color-text-primary)]">Case Summary</h2>
              <span className="font-mono text-xs text-[var(--color-text-muted)]">ID: {shortId}</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">STATUS</div>
                <div className="text-sm font-medium text-[var(--color-warning)]">{needsApproval ? 'Approval Required' : derivedStatus}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">FAILURE CODE</div>
                <div className="font-mono text-xs text-[var(--color-text-primary)] truncate" title={caseData.failure_code || 'UNKNOWN'}>
                  {caseData.failure_code || 'UNKNOWN'}
                </div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">CREATED</div>
                <div className="text-sm text-[var(--color-text-primary)]">{createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">UPDATED</div>
                <div className="text-sm text-[var(--color-text-primary)]">{updatedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
              </div>
            </div>
          </section>

          {/* Observed Evidence */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <div className="mb-6">
              <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)]">OBSERVED EVIDENCE</h2>
              <p className="text-xs text-[var(--color-text-secondary)] mt-1">Evidence available to the recovery decision.</p>
            </div>
            
            <div className="grid grid-cols-2 gap-y-6 gap-x-8 text-sm">
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Previous failed attempts</span>
                <span className="font-mono font-medium text-[var(--color-text-primary)]">{caseData.historical_failure_count || 0}</span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Last attempt</span>
                <span className="font-medium text-[var(--color-text-primary)]">
                  {caseData.events && caseData.events.length > 0 
                    ? new Date(caseData.events[caseData.events.length - 1].occurred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                    : 'Unknown'}
                </span>
              </div>
              
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Gateway status</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Operational
                </span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Failure code</span>
                <span className="font-mono text-xs text-[var(--color-text-primary)] truncate max-w-[150px]">{caseData.failure_code || 'UNKNOWN'}</span>
              </div>
              
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Opportunity amount</span>
                <span className="font-medium text-[var(--color-text-primary)]">
                  <MoneyValue amountMinor={caseData.amount_minor} currency={caseData.currency} /> {caseData.currency}
                </span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Historical failure count</span>
                <span className="font-mono font-medium text-[var(--color-text-primary)]">{caseData.historical_failure_count || 0}</span>
              </div>
            </div>
          </section>

          {/* Recovery Recommendation */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)]">RECOVERY RECOMMENDATION</h2>
              {caseData.provenance ? (
                <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded ${
                  caseData.provenance === 'Gemini' 
                    ? 'bg-[var(--color-primary-bg)] text-[var(--color-primary)] border border-[var(--color-primary)]/20' 
                    : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]'
                }`}>
                  {caseData.provenance}
                </span>
              ) : null}
            </div>

            <div className="flex justify-between items-end mb-4">
              <div>
                <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-2">RECOMMENDED ACTION</div>
                <div className="font-mono text-[var(--color-primary)] text-lg">
                  {caseData.recommendation || 'N/A'}
                </div>
              </div>
              {caseData.confidence && (
                <div className="text-right">
                  <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-2">CONFIDENCE</div>
                  <div className="font-bold text-[var(--color-success)] text-xl">
                    {Math.round(caseData.confidence * 100)}%
                  </div>
                </div>
              )}
            </div>

            <div className="bg-[var(--color-bg)] p-4 rounded-lg border border-[var(--color-border-subtle)] mb-4">
              <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-2">REASONING</div>
              <p className="text-sm text-[var(--color-text-primary)] leading-relaxed">
                {caseData.reasoning || 'No intelligence reasoning available.'}
              </p>
            </div>

            <p className="text-[11px] text-[var(--color-text-muted)] italic">
              AI recommendation is subject to policy validation and, when required, human approval.
            </p>
          </section>

          {/* Policy Checks */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)]">POLICY CHECKS</h2>
              {caseData.policy_decision === 'APPROVE' || caseData.policy_decision === 'REQUIRE_APPROVAL' ? (
                <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded border border-[var(--color-success)]/30 text-[var(--color-success)]">
                  <CheckCircle className="w-3 h-3" />
                  POLICY VALIDATED
                </span>
              ) : (
                <span className="text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded border border-[var(--color-border)] text-[var(--color-text-secondary)]">
                  {caseData.policy_decision || 'PENDING'}
                </span>
              )}
            </div>
            
            <div className="space-y-3">
              {caseData.policy_reasons && caseData.policy_reasons.length > 0 ? (
                caseData.policy_reasons.map((reason: string, i: number) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">{reason}</span>
                  </div>
                ))
              ) : (
                <>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">Amount within limit</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">Currency matches</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">No active fraud flags</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">Recovery attempt within policy</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0" />
                    <span className="text-sm text-[var(--color-text-secondary)]">No conflicting active recovery</span>
                  </div>
                </>
              )}
            </div>
          </section>

          {/* Human Approval Required */}
          {needsApproval && (
            <section className="p-6 rounded-xl border border-[var(--color-warning)]/50 bg-[var(--color-surface)] shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-[var(--color-warning)]"></div>
              
              <div className="flex items-start gap-3 mb-4">
                <AlertTriangle className="w-5 h-5 text-[var(--color-warning)] shrink-0 mt-0.5" />
                <div>
                  <h2 className="text-base font-bold font-display uppercase tracking-wider text-[var(--color-warning)] mb-1">
                    HUMAN APPROVAL REQUIRED
                  </h2>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    This recovery action requires operator approval before financial execution.
                    <br/>
                    Approval authorizes the proposed recovery action to proceed to the execution stage.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 mt-6 lg:ml-8 flex-wrap">
                <button 
                  className="px-4 py-2 text-sm font-medium border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  Review Case
                </button>
                <button 
                  className="px-4 py-2 text-sm font-medium border border-[var(--color-border-subtle)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-warning)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-warning)]"
                >
                  Reject
                </button>
                <button 
                  onClick={handleApprove}
                  disabled={approving || !caseData.action_id}
                  className="px-6 py-2 text-sm font-medium bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary)]/90 transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {approving ? 'Authorizing...' : 'Approve Recovery'}
                </button>
              </div>
            </section>
          )}
        </div>

        {/* RIGHT COLUMN */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Lifecycle */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)] mb-6">Recovery Case Timeline</h2>
            <RecoveryJourney currentState={caseData.workflow_state || ''} timeline={caseData.timeline || []} />
          </section>

          {/* System Context */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)] mb-6">SYSTEM CONTEXT</h2>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Gemini LLM</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Available
                </span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Policy Engine</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Operational
                </span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">n8n Workflow</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Connected
                </span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-border-subtle)] pb-2">
                <span className="text-[var(--color-text-secondary)]">Razorpay Test</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Connected
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[var(--color-text-secondary)]">Verification</span>
                <span className="flex items-center gap-1.5 text-[var(--color-success)] text-xs font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Operational
                </span>
              </div>
            </div>
          </section>

          {/* Recent Activity */}
          <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)] mb-6">RECENT ACTIVITY</h2>
            <div className="space-y-4">
              {timeline.slice(0, 5).map((event, i) => (
                <div key={i} className="flex gap-4 items-start border-l-2 border-[var(--color-border-subtle)] pl-3">
                  <div className="w-16 shrink-0 font-mono text-[10px] text-[var(--color-text-muted)] mt-0.5">
                    {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className={`text-sm ${
                    event.event_type.includes('APPROVAL_REQUIRED') ? 'text-[var(--color-warning)] font-medium' :
                    event.event_type.includes('RECOMMENDATION') ? 'text-[var(--color-text-primary)]' :
                    'text-[var(--color-text-secondary)]'
                  }`}>
                    {event.event_type.replace(/_/g, ' ')}
                  </div>
                </div>
              ))}
              {timeline.length === 0 && (
                <div className="text-sm text-[var(--color-text-muted)]">No recent activity.</div>
              )}
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
