with open("frontend/src/pages/AuditPage.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Pass allEvents to SelectedEventPanel
content = content.replace(
    "<SelectedEventPanel event={selectedEvent} />",
    "<SelectedEventPanel event={selectedEvent} allEvents={events} />"
)

# Update SelectedEventPanel signature
content = content.replace(
    "function SelectedEventPanel({ event }: { event: any }) {",
    "function SelectedEventPanel({ event, allEvents }: { event: any, allEvents: any[] }) {"
)

# Replace the fake lifecycle trace
bad_trace = """        <div className="space-y-4 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-[var(--color-border-subtle)]">
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-4 h-4 rounded-full bg-[var(--color-success)] flex items-center justify-center shrink-0"><div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div></div>
            <span className="text-xs text-[var(--color-text-primary)]">Detected to Human Approval</span>
          </div>
          <div className="flex items-center gap-3 relative z-10">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${isExecution ? 'bg-[var(--color-primary)] border-4 border-[var(--color-bg)]' : 'bg-[var(--color-border)]'}`}></div>
            <span className={`text-xs font-bold ${isExecution ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-muted)]'}`}>Execution Queued</span>
          </div>
          <div className="flex items-center gap-3 relative z-10">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${event.event_type.includes('VERIFICATION') ? 'bg-[var(--color-primary)] border-4 border-[var(--color-bg)]' : 'bg-[var(--color-border)]'}`}></div>
            <span className={`text-xs font-medium ${event.event_type.includes('VERIFICATION') ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-muted)]'}`}>Provider Response to Outcome</span>
          </div>
        </div>"""

good_trace = """        <div className="space-y-4 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-[var(--color-border-subtle)]">
          {allEvents.filter(e => e.case_id === event.case_id).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()).map((e, i) => (
            <div key={e.audit_event_id} className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${e.audit_event_id === event.audit_event_id ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-border)]'}`}>
                {e.audit_event_id === event.audit_event_id && <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>}
              </div>
              <span className={`text-xs ${e.audit_event_id === event.audit_event_id ? 'text-[var(--color-primary)] font-bold' : 'text-[var(--color-text-primary)]'}`}>
                {e.event_type}
              </span>
            </div>
          ))}
        </div>"""

if bad_trace in content:
    content = content.replace(bad_trace, good_trace)
    with open("frontend/src/pages/AuditPage.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed Audit Trace to use real events.")
else:
    print("Could not find the fake trace.")
