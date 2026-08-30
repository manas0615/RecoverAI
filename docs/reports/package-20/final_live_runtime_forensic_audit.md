# P20 FINAL LIVE RUNTIME FORENSIC AUDIT

## 1. Repository SHA
Current HEAD: `99bcd5ff55896d5302a732d7dd98a3ebbd4e7462`

## 2. Runtime environment
Backend: FastAPI running on Windows PowerShell (via `start-all.ps1`).

## 3. Browser environment
Frontend: Vite + React on `http://localhost:5173`.

## 4. Backend health
Operational, but subject to systemic 500 errors on specific endpoints (`/analyze`) due to serialization/model discrepancies.

## 5. Frontend health
Operational, but missing major required sections (Charts, Evidence UI) and employing non-compliant error handling (native alerts).

## 6. Analyze Case HTTP trace
1. **Browser**: User clicks "Analyze Case" in `CaseDetailView.tsx`.
2. **Frontend Client**: `apiClient.analyzeCase(id)` issues `POST /recovery-cases/{case_id}/analyze`.
3. **API Route**: `analyze_case` in `recoverai/api/main.py`.
4. **AppContainer / Domain**: `container.intelligence.analyze` executes and successfully falls back to Deterministic mode (due to missing API keys).
5. **Policy Engine**: `container.policy.evaluate` successfully generates a `PolicyDecision`.
6. **Exception**: The API route tries to serialize the audit event using `decision.reasons`, which does not exist (`reason_codes` is the correct attribute).
7. **HTTP Response**: The route catches the `AttributeError`, logs it, and returns `HTTP 500: {"detail": "Analysis unavailable"}`.
8. **Frontend Rendering**: `CaseDetail.tsx` catches the error and fires `alert('Analysis unavailable')`.

## 7. Analyze Case root cause
**API Route / Serialization Error:** The route `recoverai/api/main.py` explicitly accesses `decision.reasons`, but the `PolicyDecision` domain object defines `reason_codes`. This causes an `AttributeError` before the transaction can commit.

## 8. LLM Gateway runtime behavior
The Gateway correctly intercepts the lack of API keys, fails gracefully (`GatewayError`), and the Intelligence Analyzer successfully routes to its deterministic fallback method (`_deterministic_cause_assessment`). The failure is NOT in the LLM Gateway.

## 9. Database inventory
- **RecoveryCases**: 13 (Expected 7)
The additional cases (`case_pay_...`, `case_approval_...`) were injected during the automated test run (`uv run pytest`).

## 10. Seed behavior
The seed script (`scripts/seed_demo_data.py`) correctly deletes all tables and inserts exactly 7 cases. It is fully idempotent. However, automated integration tests instantiate the global `settings` object before `conftest.py` can patch `DATABASE_URL`, polluting the production SQLite database (`recoverai.db`).

## 11. Dashboard metric audit
| Metric | Source | Implemented | API Supported | Runtime Value | UI Visual | Truthful |
| --- | --- | --- | --- | --- | --- | --- |
| Revenue at Risk | Computed from `OPEN` cases | Yes | Yes | Dynamic | KPI Card | Yes |
| Verified Recovered | Computed from `RECOVERED` cases | Yes | Yes | Dynamic | KPI Card | Yes |
| Active Cases | Computed from `OPEN` cases | Yes | Yes | Dynamic | KPI Card | Yes |
| Recovery Rate | N/A | No | No | `DATA UNAVAILABLE` | KPI Card | Yes |
| Recovery Pipeline | N/A | No | No | N/A | Missing | N/A |
| Failed Recovery | N/A | No | No | N/A | Missing | N/A |

## 12. Chart/analytics audit
| Metric | Implemented | UI Visual | Truthful |
| --- | --- | --- | --- |
| Outcome Distribution | No | Missing | N/A |
| Recovery Funnel | No | Missing | N/A |
| Recovery Over Time | No | Missing | N/A |
**Verdict:** Charts were never implemented in the frontend.

## 13. Case Detail section audit
| Section | Source Component | Visible to User | Status |
| --- | --- | --- | --- |
| Case Context | `CaseSummary` | Yes | IMPLEMENTED |
| Evidence | N/A | No | MISSING |
| Analyze | `Analyze Button` | Yes | IMPLEMENTED (Backend fails) |
| AI Intelligence | `AI Suggests` | Yes | IMPLEMENTED (Requires payload) |
| Policy Decision | `Policy Decides` | Yes | IMPLEMENTED (Requires payload) |
| Execution | `System Executes` | Yes | IMPLEMENTED (Requires payload) |
| Verification | `Verification Proves` | Yes | IMPLEMENTED (Requires payload) |
| Audit | `Timeline` | Yes | IMPLEMENTED |

## 14. Evidence-first audit
**MISSING.** The frontend completely omits the raw `RevenueEvent` payload prior to analysis. The story jumps from `Case Summary` directly to the `Analyze Case` button.

## 15. Cases triage audit
- **Filtering:** No visible state or amount filters.
- **Sorting:** No visible sorting controls.
- **Search:** No search bar.
- **Controls Visible:** Only a raw HTML table with pagination/slice.
**Verdict:** Bare-minimum table implementation. Missing triage UX.

## 16. Error UX audit
**Actual behavior:** Native browser `alert("Analysis unavailable")`.
**Source:** `frontend/src/pages/CaseDetail.tsx`.
**Desired behavior from P20:** Seamless inline UI feedback (e.g., Toast or error-state button) without blocking the browser thread.

## 17. Warm Premium audit
**Verdict:** The core aesthetic (beige/cream, rounded borders, clean typography) is preserved. No cyber/dark themes introduced. 

## 18. Responsive runtime audit
**Verdict:** The UI scales correctly on mobile, tablet, and desktop without horizontal overflow.

## 19. Security runtime audit
**Verdict:** `.env` and `*.db` are ignored. No secrets are leaked in the codebase.

## 20. P20 report contradiction matrix
| P20 Claim | Source Reality | Runtime Reality | Verdict |
| --- | --- | --- | --- |
| Dashboard Analytics / Charts | No charts exist in code | No charts in browser | **FALSE** |
| Evidence-first UI | Missing from CaseDetailView | Hidden until AI executes | **FALSE** |
| Analyze Case works | Code fails on `decision.reasons` | HTTP 500 / Browser Alert | **FALSE** |
| Cases filtering intact | Hardcoded slice only | No filters visible | **FALSE** |
| Demo dataset (7 cases) | Tests pollute DB | 13 cases in UI | **PARTIALLY TRUE** |
| P14 Evaluation | Script missing / fails | Fails to execute | **NOT EXECUTED** |

## 21. Exact blockers
1. `AttributeError` in `recoverai/api/main.py` causing 500 on Analyze Case.
2. Integration tests polluting `recoverai.db` due to global `settings` instantiation order.
3. Missing "Evidence" rendering in Case Detail before Analyze Case.
4. Missing Dashboard Charts (Outcome Distribution, Funnel).
5. Native `alert()` error UX on failure.

## 22. Exact non-blockers
1. Actual AI execution (fallback handles safely).
2. Razorpay execution (mock adapter handles safely).

## 23. Required corrections
1. Fix `recoverai/api/main.py` to use `decision.reason_codes`.
2. Fix `recoverai/config.py` and `conftest.py` to prevent test DB pollution.
3. Add a dedicated `Evidence` section (rendering source events) to `CaseDetailView.tsx`.
4. Implement Recharts (or similar) for Dashboard charts.
5. Replace `alert()` with semantic inline feedback.
6. Add basic state filtering to the Cases table.

## 24. P20 readiness score
40/100. Core architecture is sound, but product finish and runtime integration are broken.

## 25. Final readiness decision
READY AFTER TARGETED CORRECTIONS
