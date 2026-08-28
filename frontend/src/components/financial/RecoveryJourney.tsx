import { Check, AlertTriangle, X } from 'lucide-react';

interface RecoveryJourneyProps {
  currentState: string;
}

const STAGES = [
  { id: 'DETECTED', label: 'Detected', states: ['DETECTED'] },
  { id: 'ASSESSED', label: 'Assessed', states: ['ENRICHING', 'ASSESSED'] },
  { id: 'POLICY', label: 'Policy', states: ['PLANNING', 'POLICY_REVIEW', 'WAITING_APPROVAL', 'ESCALATED'] },
  { id: 'EXECUTING', label: 'Executing', states: ['EXECUTING', 'ACTION_EXECUTING', 'UNKNOWN', 'ACTION_EXECUTION_UNKNOWN'] },
  { id: 'VERIFYING', label: 'Verifying', states: ['VERIFYING', 'VERIFICATION_STARTED', 'VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE'] },
];

export function RecoveryJourney({ currentState }: RecoveryJourneyProps) {
  const isFailed = ['VERIFIED_FAILURE', 'NOT_RECOVERED', 'SUPPRESSED'].includes(currentState);
  const isUnknown = currentState === 'UNKNOWN';
  const isSuccess = ['VERIFIED_SUCCESS', 'RECOVERED', 'CLOSED'].includes(currentState) && !isFailed && !isUnknown;
  const isEscalated = currentState === 'ESCALATED';
  const isWaitingApproval = currentState === 'WAITING_APPROVAL';

  // Find current active stage index
  let activeIndex = STAGES.findIndex(s => s.states.includes(currentState));
  if (activeIndex === -1 && (isSuccess || isFailed)) {
    activeIndex = STAGES.length - 1; // Last step
  }
  
  return (
    <div className="flex items-center justify-between w-full max-w-3xl mx-auto py-6">
      {STAGES.map((stage, index) => {
        const isCompleted = index < activeIndex || (index === activeIndex && isSuccess);
        const isActive = index === activeIndex && !isSuccess;
        
        // Custom states for active/completed based on specific statuses
        let circleClass = 'bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-muted)]';
        let lineClass = 'bg-[var(--color-border-subtle)]';
        let Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;

        if (isCompleted) {
          circleClass = 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white';
          lineClass = 'bg-[var(--color-primary)]';
          Icon = () => <Check className="w-4 h-4" />;
        } else if (isActive) {
          if (isFailed) {
            circleClass = 'bg-[var(--color-danger-bg)] border-[var(--color-danger)] text-[var(--color-danger)] ring-4 ring-[var(--color-danger-bg)]';
            Icon = () => <X className="w-4 h-4" />;
          } else if (isUnknown || isEscalated || isWaitingApproval) {
            circleClass = 'bg-[var(--color-warning-bg)] border-[var(--color-warning)] text-[var(--color-warning)] ring-4 ring-[var(--color-warning-bg)]';
            Icon = () => (isWaitingApproval ? <span className="w-2 h-2 rounded-full bg-current animate-pulse" /> : <AlertTriangle className="w-4 h-4" />);
          } else {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-primary)] text-[var(--color-primary)] ring-4 ring-[var(--color-primary-bg)]';
          }
        }
        
        return (
          <div key={stage.id} className="flex flex-col items-center relative flex-1">
            {/* Connecting line */}
            {index < STAGES.length - 1 && (
              <div 
                className={`absolute top-4 left-[50%] right-[-50%] h-[2px] transition-colors duration-500 ${lineClass}`}
              />
            )}
            
            {/* Step circle */}
            <div 
              className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300 ${circleClass}`}
            >
              <Icon />
            </div>
            
            <span className={`mt-3 text-xs font-medium tracking-wide uppercase transition-colors ${
              isCompleted || isActive ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)]'
            }`}>
              {stage.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
