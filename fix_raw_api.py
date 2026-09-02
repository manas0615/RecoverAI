with open("frontend/src/pages/VerificationQueue.tsx", "r", encoding="utf-8") as f:
    content = f.read()

bad_code = """      {/* Actions */}
      <div className="p-4 bg-[var(--color-bg)] flex gap-3">
        <button className="flex-1 px-4 py-2 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors focus:outline-none">
          View Raw API
        </button>"""

good_code = """      {/* Actions */}
      <div className="p-4 bg-[var(--color-bg)] flex gap-3">"""

if bad_code in content:
    content = content.replace(bad_code, good_code)
    with open("frontend/src/pages/VerificationQueue.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed fake Raw API button.")
else:
    print("Could not find the block in VerificationQueue.")
