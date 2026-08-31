import re

with open('frontend/src/pages/ApprovalQueue.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Make the right pane wrapper sticky
content = content.replace(
    '<div className="w-full lg:w-[400px] shrink-0">',
    '<div className="w-full lg:w-[400px] shrink-0 sticky top-6 self-start">'
)

# Extract everything from `const isApproved = c.workflow_state !== 'WAITING_APPROVAL';` to the end of the file
# and replace the `return (...)` of `SelectedApprovalPanel`.

start_idx = content.find("const isApproved = c.workflow_state !== 'WAITING_APPROVAL';")
return_idx = content.find("return (", start_idx)
end_idx = content.rfind("}")

new_return = """return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)] flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Lock className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h2 className="font-mono font-bold text-[var(--color-text-primary)] text-lg">{shortId}</h2>
            {isApproved ? (
              <StatusBadge status="AUTHORIZED" />
            ) : (
              <StatusBadge status="APPROVAL_REQUIRED" />
            )}
          </div>
          <div className="grid grid-cols-[100px_1fr] gap-y-2 text-sm">
            <div className="text-[var(--color-text-secondary)]">Amount at Risk:</div>
            <div className="font-medium text-[var(--color-text-primary)] text-right">
              <MoneyValue amountMinor={c.amount_minor} currency={c.currency} /> {c.currency}
            </div>
            <div className="text-[var(--color-text-secondary)]">Failure:</div>
            <div className="font-mono text-xs text-red-400 text-right truncate" title={c.failure_code || 'UNKNOWN'}>
              {c.failure_code || 'UNKNOWN'}
            </div>
          </div>
        </div>
        <button onClick={onClose} className="p-1 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex flex-col">
        {/* Observed Evidence */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">OBSERVED EVIDENCE</h3>
          </div>
          <div className="grid grid-cols-2 gap-y-4 gap-x-4 text-xs">
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Previous Attempts</div>
              <div className="font-medium text-[var(--color-text-primary)]">{c.historical_failure_count || 0}</div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Last Attempt</div>
              <div className="font-medium text-[var(--color-warning)]">
                {c.events && c.events.length > 0 
                  ? new Date(c.events[c.events.length - 1].occurred_at || c.events[c.events.length - 1].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                  : 'Unknown'}
              </div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Gateway Status</div>
              <div className="font-medium text-[var(--color-success)]">Operational</div>
            </div>
            <div>
              <div className="text-[var(--color-text-secondary)] mb-1">Historical Falls</div>
              <div className="font-medium text-[var(--color-text-primary)]">{c.historical_failure_count || 0}</div>
            </div>
          </div>
        </div>

        {/* Gemini Recommendation */}
        <div className="p-4 bg-[var(--color-primary)]/5 border-b border-[var(--color-border-subtle)]">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 flex items-center justify-center text-[var(--color-primary)]">✧</div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-primary)]">{c.provenance || 'AI'} Recommendation</h3>
            </div>
            {c.confidence && (
              <span className="text-[10px] font-bold bg-[var(--color-primary)]/10 text-[var(--color-primary)] px-2 py-0.5 rounded">
                {Math.round(c.confidence * 100)}% CONFIDENCE
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-[var(--color-primary)] font-bold mb-3">
            &gt; {c.recommendation || 'N/A'}
          </div>
          <p className="text-xs text-[var(--color-text-primary)] italic leading-relaxed mb-3">
            "{c.reasoning || 'No intelligence reasoning available.'}"
          </p>
          <div className="text-[9px] uppercase tracking-wider text-[var(--color-text-muted)]">
            DISCLAIMER: AI RECOMMENDATION IS SUBJECT TO POLICY VALIDATION AND HUMAN APPROVAL.
          </div>
        </div>

        {/* Policy Validation */}
        <div className="p-4 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">POLICY VALIDATION</h3>
            </div>
            <span className="text-[10px] font-bold bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30 px-2 py-0.5 rounded uppercase">
              {c.policy_decision === 'APPROVE' || c.policy_decision === 'REQUIRE_APPROVAL' ? 'PASSED' : (c.policy_decision || 'PENDING')}
            </span>
          </div>
          <div className="space-y-3">
            {c.policy_reasons && c.policy_reasons.length > 0 ? (
              c.policy_reasons.map((reason: string, i: number) => (
                <div key={i} className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">{reason}</span>
                </div>
              ))
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Amount within configured limit</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Currency matches case</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">No active fraud flags</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">Recovery attempt within policy</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--color-success)] shrink-0" />
                  <span className="text-xs text-[var(--color-text-secondary)]">No conflicting active recovery</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Lifecycle / Authorization */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-[var(--color-text-secondary)]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-text-primary)]">LIFECYCLE</h3>
          </div>
          
          {isApproved ? (
            <div className="pl-3 border-l-2 border-[var(--color-success)]">
              <h4 className="text-xs font-bold text-[var(--color-success)] uppercase tracking-wider mb-1">
                ACTION AUTHORIZED
              </h4>
              <p className="text-[11px] text-[var(--color-text-secondary)]">
                The recovery action was approved and has progressed to execution.
              </p>
            </div>
          ) : (
            <div className="pl-3 border-l-2 border-[var(--color-warning)]">
              <div className="flex items-start gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-[var(--color-warning)] shrink-0" />
                <div>
                  <h4 className="text-[11px] font-bold font-display uppercase tracking-wider text-[var(--color-warning)] mb-1">
                    OPERATOR AUTHORIZATION REQUIRED
                  </h4>
                  <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
                    This recovery action requires operator approval before financial execution.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 mt-5">
                <button className="px-4 py-2 text-xs font-medium border border-[var(--color-border-subtle)] rounded hover:bg-[var(--color-surface-secondary)] text-red-400 transition-colors focus:outline-none">
                  <span className="mr-1">⊘</span> REJECT
                </button>
                <button 
                  onClick={handleApprove}
                  disabled={approving || !c.action_id}
                  className="flex-1 px-4 py-2 text-xs font-bold bg-[var(--color-primary)] text-[var(--color-bg)] rounded hover:bg-[var(--color-primary)]/90 transition-colors focus:outline-none disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  {approving ? 'AUTHORIZING...' : 'APPROVE RECOVERY'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}"""

content = content[:return_idx] + new_return

with open('frontend/src/pages/ApprovalQueue.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
