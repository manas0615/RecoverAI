import re

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the generation of future nodes
old_future = '''    for (let i = maxStageReached + 1; i < STAGES.length; i++) {
      nodes.push({
        type: 'future',
        data: STAGES[i],
        isLastEvent: false,
        index: nodes.length
      });
    }'''

new_future = '''    let stopped = false;
    const policyDecisionEvent = timeline.find(e => e.event_type === 'POLICY_DECISION_CREATED');
    let decision = null;
    if (policyDecisionEvent) {
      decision = policyDecisionEvent.metadata?.decision;
      if (decision === 'DENY' || decision === 'SUPPRESS') stopped = true;
    }
    
    if (!stopped) {
      for (let i = maxStageReached + 1; i < STAGES.length; i++) {
        let stage = {...STAGES[i]};
        let isSyntheticCurrent = false;
        
        if (decision === 'APPROVE' && i === 3) {
           // Skip human approval if approved
           continue; 
        }
        if (decision === 'APPROVE' && i === 4 && maxStageReached === 2) {
           stage.label = 'Ready for Execution';
           isSyntheticCurrent = true;
        }
        if (decision === 'ESCALATE' && i === 3 && maxStageReached === 2) {
           isSyntheticCurrent = true;
        }

        nodes.push({
          type: 'future',
          data: stage,
          isLastEvent: isSyntheticCurrent,
          index: nodes.length
        });
        
        if (decision === 'APPROVE' && i === 4 && maxStageReached === 2) {
           break; // Stop at Ready for Execution according to instructions
        }
      }
    }'''

content = content.replace(old_future, new_future)

# Then we need to handle rendering of 'future' node if it is synthetic current
old_future_render = '''        if (node.type === 'future') {
          const stage = node.data;
          return (
            <div key={stage.id} className="relative flex items-start group min-h-[3rem]">
              <div className="relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-muted)] shrink-0 mr-4 transition-colors duration-300">
                <span className="w-2 h-2 rounded-full bg-current" />
              </div>
              <div className="flex-1 pb-4">
                <h4 className="text-sm font-medium transition-colors text-[var(--color-text-secondary)]">
                  {stage.label}
                </h4>
              </div>
            </div>
          );
        }'''

new_future_render = '''        if (node.type === 'future') {
          const stage = node.data;
          let circleClass = "border-[var(--color-border)] text-[var(--color-text-muted)]";
          let textClass = "text-[var(--color-text-secondary)]";
          if (node.isLastEvent) {
             circleClass = "border-[var(--color-primary)] text-[var(--color-primary)]";
             textClass = "text-[var(--color-primary)] font-bold";
          }
          return (
            <div key={stage.id} className="relative flex items-start group min-h-[3rem] animate-in fade-in slide-in-from-top-4 duration-500 fill-mode-both" style={{ animationDelay: node.index * 100 + 'ms' }}>
              <div className={"relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>
                <span className="w-2 h-2 rounded-full bg-current" />
              </div>
              <div className="flex-1 pb-4">
                <h4 className={"text-sm font-medium transition-colors " + textClass}>
                  {stage.label} {node.isLastEvent && <span className="text-[10px] font-bold uppercase tracking-wider ml-1 opacity-70">— CURRENT</span>}
                </h4>
              </div>
            </div>
          );
        }'''
content = content.replace(old_future_render, new_future_render)

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
