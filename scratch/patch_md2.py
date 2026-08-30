import re

with open("scratch/report_temp.md", "r", encoding="utf-16") as f:
    content = f.read()

# 1. Update Section 13 (Reproducibility Statement)
content = re.sub(
    r"(13\. REPRODUCIBILITY RESULT\n=+\n)Safe testing demonstrated that running the patched `scripts/seed_demo_data\.py` produces the exact intended outcome states without duplicate insertions or FK violations\.",
    r"\1The corrected seed script was safely validated to generate exactly 7 curated scenarios with no duplicate insertions, no FK violations, coherent state transitions, and coherent audit metadata.",
    content,
)

# 2. Update Section 14 (Contradiction Matrix)
old_matrix = """- "7 curated scenarios": TRUE.
- "SUCCESS": PARTIALLY TRUE (UI failed to parse Verification state due to audit mismatch).
- "FAILURE": FALSE (Was originally stuck in `DETECTED`/`OPEN`).
- "UNKNOWN": FALSE (Was originally stuck in `DETECTED`/`OPEN`).
- "DENIAL": FALSE (Was originally stuck in `DETECTED`/`OPEN`).
- "ESCALATION": FALSE (Was originally incorrectly executed instead of waiting).
- "DUPLICATE": TRUE.
- "LIVE": TRUE."""

new_matrix = """**BEFORE CORRECTION:**
- "7 curated scenarios": TRUE.
- "SUCCESS": PARTIALLY TRUE (UI failed to parse Verification state due to audit mismatch).
- "FAILURE": FALSE (Was originally incorrectly left DETECTED/OPEN).
- "UNKNOWN": FALSE (Was originally incorrectly left DETECTED/OPEN).
- "DENIAL": FALSE (Was originally incorrectly left DETECTED/OPEN).
- "ESCALATION": FALSE (Was originally incorrectly marked as executing instead of waiting).
- "DUPLICATE": TRUE.
- "LIVE": TRUE.

**AFTER CORRECTION:**
All seven curated scenarios now match their intended semantics."""

content = content.replace(old_matrix, new_matrix)

# 3. Update Section 15 and 16 (Preserve forensic history with labels)
old_15_16 = """======================================================================
15. EXACT DEFECTS FOUND
======================================================================
1. `case_FAILURE`, `case_UNKNOWN`, and `case_DENIAL` were not correctly progressed via the State Machine and were incorrectly left `OPEN` at `DETECTED`.
2. `case_ESCALATION` incorrectly received `action.begin_execution` despite being escalated for human review.
3. The `add_audit` helper function ignored `new_state` and `previous_state`, leaving the frontend `CaseDetailView.tsx` parsing `VERIFICATION_COMPLETED` as `UNKNOWN`.

======================================================================
16. EXACT CORRECTIONS MADE
======================================================================
1. **Added explicit State Machine progressions** in `seed_demo_data.py` to ensure cases reach their semantic definitions (`CLOSED`/`UNKNOWN`/`WAITING_APPROVAL`).
2. **Removed execution logic** from the Escalation case seed to ensure it remains in a proposed state.
3. **Patched the `add_audit` method** to pop and assign `new_state` and `previous_state` explicitly to the `AuditEvent` constructor."""

new_15_16 = """======================================================================
15. EXACT DEFECTS FOUND
======================================================================
- **ORIGINAL DEFECT**: `case_FAILURE`, `case_UNKNOWN`, and `case_DENIAL` were originally left incorrectly open (stuck at `DETECTED` and `OPEN`).
- **ORIGINAL DEFECT**: `case_ESCALATION` originally contained invalid execution behavior (`action.begin_execution`).
- **ORIGINAL DEFECT**: `add_audit` originally ignored state metadata (`new_state` and `previous_state`), leaving `CaseDetailView.tsx` parsing `VERIFICATION_COMPLETED` as `UNKNOWN`.

======================================================================
16. EXACT CORRECTIONS MADE
======================================================================
- **CORRECTION**: Added explicit State Machine progressions in `seed_demo_data.py` to ensure `case_FAILURE`, `case_UNKNOWN`, and `case_DENIAL` reach their semantic definitions.
- **CORRECTION**: Removed execution logic from the `case_ESCALATION` seed to ensure it appropriately remains in a proposed state.
- **CORRECTION**: Patched the `add_audit` method to pop and assign `new_state` and `previous_state` explicitly to the `AuditEvent` constructor.
- **FINAL STATE**: All seven curated scenarios now match their semantic definitions. The domain graph, state machine, and audit records are coherent and correctly rendered in the frontend."""

content = content.replace(old_15_16, new_15_16)

# 4. Update Section 20 (Remaining Limitations)
content = content.replace(
    "None. The data represents 100% domain truth.",
    "None. No known internal consistency issues remain in the curated demo dataset. The seeded records represent deterministic application scenarios and are not claimed to be live provider events.",
)

# 5. Update Section 30 (Final Freeze Decision)
content = re.sub(
    r"(30\. FINAL FREEZE DECISION\n=+\n)A\. P22 DATA MODEL VERIFIED.*?SAFE TO FREEZE",
    r"\1A. P22 DATA MODEL VERIFIED — SAFE TO FREEZE\n\n*Note: This strictly verifies the underlying data consistency and domain correctness. It does NOT claim that REAL AI VERIFIED, REAL GEMINI VERIFIED, RAZORPAY VERIFIED, or LIVE WEBHOOK VERIFIED. Those remain separate future validation stages.*",
    content,
)

with open(
    "docs/reports/package-22/p22_final_data_reconciliation.md", "w", encoding="utf-8"
) as f:
    f.write(content)
print("done")
