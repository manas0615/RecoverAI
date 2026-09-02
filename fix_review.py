with open("frontend/src/pages/CaseDetailView.tsx", "r", encoding="utf-8") as f:
    content = f.read()

bad_review = """                <button 
                  className="px-4 py-2 text-sm font-medium border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  Review Case
                </button>"""

if bad_review in content:
    content = content.replace(bad_review, "")
    with open("frontend/src/pages/CaseDetailView.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed Review Case button.")
else:
    print("Could not find Review Case button.")
