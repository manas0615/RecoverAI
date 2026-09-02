with open("frontend/src/pages/CaseDetailView.tsx", "r", encoding="utf-8") as f:
    content = f.read()

bad_reject = """                <button 
                  className="px-4 py-2 text-sm font-medium border border-[var(--color-border-subtle)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-warning)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-warning)]"
                >
                  Reject
                </button>"""

good_reject = """                <button 
                  onClick={async () => {
                    if (confirm("Are you sure you want to reject this recovery action?")) {
                      try {
                        await apiClient.abortExecution(caseData.case_id);
                        window.location.reload();
                      } catch(e) {
                        alert("Failed to reject action.");
                      }
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium border border-[var(--color-border-subtle)] rounded hover:bg-[var(--color-surface-secondary)] text-[var(--color-warning)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-warning)]"
                >
                  Reject
                </button>"""

if bad_reject in content:
    content = content.replace(bad_reject, good_reject)
    with open("frontend/src/pages/CaseDetailView.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed Reject button.")
else:
    print("Could not find Reject button.")
