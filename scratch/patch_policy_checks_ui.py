import re

with open('frontend/src/pages/CaseDetailView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to restore the policy check UI.
# Previously I had:
#               ) : caseData.policy_reasons && caseData.policy_reasons.length > 0 ? (
#                 caseData.policy_reasons.map((reason: string, i: number) => {
#                   let Icon = CheckCircle;
#                   let colorClass = 'text-[var(--color-success)]';
#                   if (caseData.policy_decision === 'ESCALATE' || caseData.policy_decision === 'DENY' || caseData.policy_decision === 'SUPPRESS') {
#                       Icon = X;
#                       colorClass = 'text-[var(--color-danger)]';
#                   }
#                   return (
#                     <div key={i} className="flex items-center gap-3">
#                       <Icon className={\ \ shrink-0} />
#                       <span className="text-sm text-[var(--color-text-secondary)]">{reason}</span>
#                     </div>
#                   );
#                 })
#               ) : (

new_code = '''              ) : caseData.policy_reasons && caseData.policy_reasons.length > 0 ? (
                caseData.policy_reasons.map((reason: string, i: number) => {
                  let Icon = CheckCircle;
                  let colorClass = 'text-[var(--color-success)]';
                  if (caseData.policy_decision === 'ESCALATE' || caseData.policy_decision === 'DENY' || caseData.policy_decision === 'SUPPRESS') {
                      Icon = X;
                      colorClass = 'text-[var(--color-danger)]';
                  }
                  
                  if (reason === 'POLICY_APPROVED') {
                    return (
                      <div key={i} className="space-y-3">
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
                      </div>
                    );
                  }

                  return (
                    <div key={i} className="flex items-center gap-3">
                      <Icon className={w-4 h-4  shrink-0} />
                      <span className="text-sm text-[var(--color-text-secondary)]">{reason.replace(/_/g, ' ')}</span>
                    </div>
                  );
                })
              ) : ('''

# Let's do a precise string replacement
old_code_pattern = r"\)\s*:\s*caseData\.policy_reasons && caseData\.policy_reasons\.length > 0 \?\s*\(\s*caseData\.policy_reasons\.map\(\(reason: string, i: number\) => \{\s*let Icon = CheckCircle;\s*let colorClass = 'text-\[var\(--color-success\)]';\s*if \(caseData\.policy_decision === 'ESCALATE' \|\| caseData\.policy_decision === 'DENY' \|\| caseData\.policy_decision === 'SUPPRESS'\) \{\s*Icon = X;\s*colorClass = 'text-\[var\(--color-danger\)]';\s*\}\s*return \(\s*<div key=\{i\} className=\"flex items-center gap-3\">\s*<Icon className=\{\w-4 h-4 \$\{colorClass\} shrink-0\\} />\s*<span className=\"text-sm text-\[var\(--color-text-secondary\)]\">\{reason\}</span>\s*</div>\s*\);\s*\}\)\s*\)\s*:\s*\("

# If re.search finds it, replace it
match = re.search(old_code_pattern, content)
if match:
    content = content[:match.start()] + new_code + content[match.end():]
else:
    print("Could not match the old code block!")

with open('frontend/src/pages/CaseDetailView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

