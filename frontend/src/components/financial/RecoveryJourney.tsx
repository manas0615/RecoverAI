import { Check } from 'lucide-react';

interface RecoveryJourneyProps {
  currentState: string;
}

const STAGES = [
  { id: 'DETECTED', label: 'Detected', states: ['DETECTED'] },
  { id: 'ASSESSED', label: 'Assessed', states: ['ENRICHING', 'ASSESSED'] },
  { id: 'POLICY', label: 'Policy', states: ['PLANNING', 'POLICY_REVIEW', 'WAITING_APPROVAL'] },
  { id: 'EXECUTING', label: 'Executing', states: ['EXECUTING', 'ACTION_EXECUTING', 'ACTION_EXECUTION_UNKNOWN'] },
  { id: 'VERIFYING', label: 'Verifying', states: ['VERIFYING', 'VERIFICATION_STARTED'] },
];

export function RecoveryJourney({ currentState }: RecoveryJourneyProps) {
  // Determine if it's closed (Terminal)
  const isTerminal = currentState === 'CLOSED' || currentState === 'UNKNOWN';
  
  // Find current active stage index
  let activeIndex = STAGES.findIndex(s => s.states.includes(currentState));
  if (activeIndex === -1 && isTerminal) {
    activeIndex = STAGES.length; // all done
  }
  
  return (
    <div className="flex items-center justify-between w-full max-w-3xl mx-auto py-6">
      {STAGES.map((stage, index) => {
        const isCompleted = index < activeIndex || isTerminal;
        const isActive = index === activeIndex && !isTerminal;
        
        return (
          <div key={stage.id} className="flex flex-col items-center relative flex-1">
            {/* Connecting line */}
            {index < STAGES.length - 1 && (
              <div 
                className={`absolute top-4 left-[50%] right-[-50%] h-[2px] transition-colors duration-500 ${
                  isCompleted ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-border-subtle)]'
                }`}
              />
            )}
            
            {/* Step circle */}
            <div 
              className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300 ${
                isCompleted 
                  ? 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white' 
                  : isActive
                    ? 'bg-[var(--color-surface)] border-[var(--color-primary)] text-[var(--color-primary)] ring-4 ring-[var(--color-primary-bg)]'
                    : 'bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-muted)]'
              }`}
            >
              {isCompleted ? <Check className="w-4 h-4" /> : <span className="w-2 h-2 rounded-full bg-current" />}
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
