import re

with open("frontend/src/pages/CaseDetailView.tsx", "r", encoding="utf-8") as f:
    content = f.read()

execution_section = """
          {/* Execution & Verification */}
          {caseData.action_status && (
            <section className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm mb-8">
              <h2 className="text-sm font-bold font-display uppercase tracking-wider text-[var(--color-text-primary)] mb-6">EXECUTION & VERIFICATION</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Execution Status</div>
                  <div className="text-sm font-medium text-[var(--color-text-primary)] mb-4">{caseData.action_status}</div>
                  
                  {caseData.workflow_execution_reference && (
                    <>
                      <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Payment Link</div>
                      <div className="text-sm font-medium mb-4">
                        <a href={caseData.workflow_execution_reference} target="_blank" rel="noreferrer" className="text-[var(--color-primary)] hover:underline flex items-center gap-1">
                          {caseData.workflow_execution_reference}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </>
                  )}
                  
                  {caseData.external_reference && (
                    <>
                      <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Provider Reference</div>
                      <div className="text-sm font-medium text-[var(--color-text-primary)]">{caseData.external_reference}</div>
                    </>
                  )}
                </div>
                
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Verification Status</div>
                  <div className="text-sm font-medium text-[var(--color-text-primary)] mb-4">
                    {caseData.status === 'CLOSED' && caseData.outcome_type === 'RECOVERED' ? (
                      <span className="text-[var(--color-success)] flex items-center gap-1"><CheckCircle className="w-4 h-4" /> RECOVERED</span>
                    ) : caseData.status === 'CLOSED' ? (
                      <span className="text-[var(--color-warning)]">{caseData.outcome_type || 'FAILED'}</span>
                    ) : (
                      <span className="text-[var(--color-text-secondary)]">PENDING</span>
                    )}
                  </div>
                  
                  {caseData.observed_amount_minor && (
                    <>
                      <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Recovered Amount</div>
                      <div className="text-sm font-medium text-[var(--color-text-primary)]">
                        {caseData.observed_currency} {(caseData.observed_amount_minor / 100).toFixed(2)}
                      </div>
                    </>
                  )}
                </div>
              </div>
            </section>
          )}
"""

content = content.replace("          {/* Timeline */}", execution_section + "\n          {/* Timeline */}")

with open("frontend/src/pages/CaseDetailView.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated CaseDetailView.tsx")
