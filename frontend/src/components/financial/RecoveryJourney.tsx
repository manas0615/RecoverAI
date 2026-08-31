import { Check, AlertTriangle, X } from 'lucide-react';

interface RecoveryJourneyProps {
  currentState: string;
  timeline?: any[];
}

const STAGES = [
  { id: 'DETECTED', label: 'Evidence Collected', states: ['DETECTED'] },
  { id: 'ASSESSED', label: 'Recommendation', states: ['ENRICHING', 'ASSESSED'] },
  { id: 'POLICY', label: 'Policy Check', states: ['PLANNING', 'POLICY_REVIEW'] },
  { id: 'APPROVAL', label: 'Human Approval', states: ['WAITING_APPROVAL', 'ESCALATED'] },
  { id: 'EXECUTING', label: 'Execution', states: ['EXECUTING', 'ACTION_EXECUTING', 'UNKNOWN', 'ACTION_EXECUTION_UNKNOWN'] },
  { id: 'VERIFYING', label: 'Verification', states: ['VERIFYING', 'VERIFICATION_STARTED', 'VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE', 'RECOVERED', 'CLOSED'] },
];

export function RecoveryJourney({ currentState, timeline }: RecoveryJourneyProps) {
  // --- REAL TIMELINE MODE (Screen 03) ---
  if (timeline && timeline.length > 0) {
    const formatEventName = (type: string) => {
      const mapping: Record<string, string> = {
        'CASE_CREATED': 'Case Detected',
        'WEBHOOK_RECEIVED': 'Evidence Collected',
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

    const getComponent = (actorType: string, eventType: string, actorId: string) => {
      if (eventType === 'ACTION_EXECUTING' || eventType === 'RAZORPAY_REQUEST_COMPLETED') return 'RecoveryActionService';
      if (eventType === 'POLICY_DECISION_CREATED') return 'PolicyEngine';
      if (eventType === 'LLM_RECOMMENDATION_CREATED') return 'Gemini';
      if (eventType.startsWith('VERIFICATION_') || eventType.startsWith('RECOVERY_')) return 'VerificationEngine (P09)';
      if (eventType === 'ACTION_AUTHORIZED') return 'Operator';
      if (eventType === 'WEBHOOK_RECEIVED') return 'Recovery Engine';
      if (actorId === 'SYSTEM' || actorType === 'SYSTEM') return 'System';
      return actorId || actorType;
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
          
          // Special state coloring if it's the latest event
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
            }
          }

          return (
            <div key={event.audit_event_id} className="relative flex items-start group min-h-[3.5rem]">
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

  // --- MOCK/DUMMY MODE (Screen 01) ---
  const isFailed = ['VERIFIED_FAILURE', 'NOT_RECOVERED', 'SUPPRESSED'].includes(currentState);
  const isUnknown = currentState === 'UNKNOWN';
  const isSuccess = ['VERIFIED_SUCCESS', 'RECOVERED', 'CLOSED'].includes(currentState) && !isFailed && !isUnknown;
  const isEscalated = currentState === 'ESCALATED';
  const isWaitingApproval = currentState === 'WAITING_APPROVAL';
  const isApprovalStage = isEscalated || isWaitingApproval;

  let activeIndex = STAGES.findIndex(s => s.states.includes(currentState));
  if (activeIndex === -1 && (isSuccess || isFailed)) {
    activeIndex = STAGES.length - 1;
  }
  if (activeIndex === -1) activeIndex = 0; // Default fallback

  return (
    <div className="flex flex-col space-y-0 w-full relative">
      <div className="absolute top-4 bottom-4 left-[11px] w-[2px] bg-[var(--color-border-subtle)]" />
      
      {STAGES.map((stage, index) => {
        const isCompleted = index < activeIndex || (index === activeIndex && isSuccess);
        const isActive = index === activeIndex && !isSuccess;
        
        let circleClass = 'bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-muted)]';
        let Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;
        let textClass = 'text-[var(--color-text-secondary)]';
        let subtext = '';

        if (isCompleted) {
          circleClass = 'bg-[var(--color-success)] border-[var(--color-success)] text-white';
          textClass = 'text-[var(--color-text-primary)]';
          Icon = () => <Check className="w-3 h-3" />;
        } else if (isActive) {
          if (isFailed) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-danger)] text-[var(--color-danger)]';
            textClass = 'text-[var(--color-danger)]';
            Icon = () => <X className="w-3 h-3" />;
          } else if (isApprovalStage) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-warning)] text-[var(--color-warning)]';
            textClass = 'text-[var(--color-warning)]';
            subtext = 'Waiting on operator action';
            Icon = () => <AlertTriangle className="w-3 h-3" />;
          } else if (isUnknown) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-warning)] text-[var(--color-warning)]';
            textClass = 'text-[var(--color-warning)]';
            Icon = () => <AlertTriangle className="w-3 h-3" />;
          } else {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-primary)] text-[var(--color-primary)]';
            textClass = 'text-[var(--color-primary)]';
          }
        }
        
        return (
          <div key={stage.id} className="relative flex items-start group min-h-[3rem]">
            <div className={"relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>
              <Icon />
            </div>
            
            <div className="flex-1 pb-4">
              <h4 className={"text-sm font-medium transition-colors " + textClass}>
                {stage.label}
              </h4>
              {subtext && (
                <div className="text-xs text-[var(--color-text-secondary)] mt-1 whitespace-normal">
                  {subtext}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
