import { Check, X } from 'lucide-react';
import type { TimelineEvent } from '../../types/domain';

interface RecoveryJourneyProps {
  currentState: string;
  timeline?: TimelineEvent[];
}

export function RecoveryJourney({ timeline }: RecoveryJourneyProps) {
  if (!timeline || timeline.length === 0) {
    return <div className="text-sm text-[var(--color-text-muted)]">No timeline events available.</div>;
  }

  const formatEventName = (type: string) => {
    const mapping: Record<string, string> = {
      'CASE_CREATED': 'Case Detected',
      'WEBHOOK_RECEIVED': 'Evidence Collected',
      'ANALYSIS_STARTED': 'Analysis Started',
      'LLM_RECOMMENDATION_CREATED': 'Recommendation Generated',
      'POLICY_DECISION_CREATED': 'Policy Check',
      'ACTION_AUTHORIZED': 'Human Approval',
      'ACTION_EXECUTING': 'Execution Queued',
      'RAZORPAY_REQUEST_COMPLETED': 'Provider Response',
      'VERIFICATION_COMPLETED': 'Recovery Outcome',
      'VERIFICATION_STARTED': 'Verification Started',
      'CASE_ESCALATED': 'Escalation Recorded',
      'RECOVERY_CONFIRMED': 'Recovery Confirmed'
    };
    return mapping[type] || type.replace(/_/g, ' ').toLowerCase();
  };

  const getComponent = (actorType: string | undefined | null, eventType: string, actorId: string | undefined | null) => {
    if (eventType === 'ACTION_EXECUTING' || eventType === 'RAZORPAY_REQUEST_COMPLETED') return 'RecoveryActionService';
    if (eventType === 'POLICY_DECISION_CREATED') return 'PolicyEngine';
    if (eventType === 'LLM_RECOMMENDATION_CREATED') return actorId?.includes('deterministic') ? 'Deterministic Fallback' : (actorId || 'Gemini');
    if (eventType.startsWith('VERIFICATION_') || eventType.startsWith('RECOVERY_')) return 'VerificationEngine (P09)';
    if (eventType === 'ACTION_AUTHORIZED') return 'Operator';
    if (eventType === 'WEBHOOK_RECEIVED') return 'Recovery Engine';
    if (actorId === 'SYSTEM' || actorType === 'SYSTEM') return 'System';
    return actorId || actorType || 'System';
  };

  return (
    <div className="flex flex-col space-y-0 w-full relative">
      <div className="absolute top-4 bottom-4 left-[11px] w-[2px] bg-[var(--color-border-subtle)]" />
      
      {timeline.map((event, index) => {
        const isLast = index === timeline.length - 1;
        const timeStr = new Date(event.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        const label = formatEventName(event.event_type);
        const actor = getComponent(event.actor?.type, event.event_type, event.actor?.id);
        
        let circleClass = 'bg-[var(--color-success)] border-[var(--color-success)] text-white';
        let Icon = () => <Check className="w-3 h-3" />;
        let textClass = 'text-[var(--color-text-primary)]';
        
        if (isLast) {
          if (event.event_type === 'ACTION_AUTHORIZED' || event.event_type === 'CASE_ESCALATED') {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-warning)] text-[var(--color-warning)]';
            Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;
            textClass = 'text-[var(--color-warning)] font-bold';
          } else if (event.event_type === 'VERIFICATION_COMPLETED' && event.metadata?.verified_state === 'FAILURE') {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-danger)] text-[var(--color-danger)]';
            Icon = () => <X className="w-3 h-3" />;
            textClass = 'text-[var(--color-danger)] font-bold';
          } else if (event.event_type === 'ACTION_EXECUTING' || event.event_type === 'VERIFICATION_STARTED') {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-primary)] text-[var(--color-primary)]';
            Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;
            textClass = 'text-[var(--color-primary)] font-bold';
          } else {
            // For general completed states, if it's the last node, we still might want to show it as the terminal success
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-success)] text-[var(--color-success)]';
            Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;
            textClass = 'text-[var(--color-success)] font-bold';
          }
        }

        return (
          <div key={event.audit_event_id || index} className="relative flex items-start group min-h-[3.5rem] animate-in fade-in slide-in-from-top-4 duration-500 fill-mode-both" style={{ animationDelay: index * 50 + 'ms' }}>
            <div className={"relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>
              <Icon />
            </div>
            <div className="flex-1 pb-5">
              <div className="flex items-baseline gap-2">
                <h4 className={"text-sm font-medium transition-colors " + textClass}>
                  {label} {isLast && <span className="text-[10px] font-bold uppercase tracking-wider ml-1 opacity-70">— CURRENT</span>}
                </h4>
              </div>
              <div className="flex flex-col gap-0.5 mt-0.5">
                <span className="text-xs font-mono text-[var(--color-text-secondary)]">{timeStr}</span>
                <span className="text-xs text-[var(--color-text-muted)]">{actor}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
