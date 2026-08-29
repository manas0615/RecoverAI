# PRE-P20 FINAL FRONTEND / UX / AI AUDIT IMPLEMENTATION PLAN

## 1. Executive Summary
The forensic audit reveals that while the frontend source code is largely complete, the application fails critically at runtime. A missing `frontend/.env` file causes an immediate 401 Unauthorized "Access Configuration Required" block. Furthermore, the `scripts/seed_demo_data.py` script crashes due to a SQLite Foreign Key constraint, meaning no data is seeded. Finally, the seed script completely omits AI timeline events, meaning the "AI Suggests" section is permanently empty in the UI. These issues MUST be fixed before the P20 demo.

## 2. Repository Reality
The repository contains high-quality React code (`AccessBoundary.tsx`, `CaseDetailView.tsx`), but the integration layer is broken.
- `frontend/.env` does not exist.
- `seed_demo_data.py` crashes on line 109 (`DELETE FROM recovery_cases`).
- `seed_demo_data.py` lacks `LLM_RECOMMENDATION_CREATED` inserts.

## 3. Original Product Intent
Demonstrate a 5-minute judge journey showing the bounded control loop (DETECT -> UNDERSTAND -> DECIDE -> AUTHORIZE -> ACT -> VERIFY). 

## 4. Current Frontend Architecture
React 19, TypeScript, Vite, TailwindCSS v4. It expects `VITE_API_KEY` to authenticate with the backend via `X-API-Key` headers.

## 5. Route Inventory
- `/` - Dashboard
- `/cases` - Case List
- `/cases/:id` - Case Detail
- `/system` - System Health
- `/fixtures` - UI State Fixtures

## 6. 401 Root Cause
**CONFIRMED BY RUNTIME:** The file `frontend/.env` is missing. The `VITE_API_KEY` is undefined. The backend `require_frontend_key` dependency rejects the empty header with 401 Unauthorized, triggering the `AccessBoundary` UI.

## 7. 403 Handling
**CONFIRMED BY SOURCE:** Handled correctly. If the frontend attempts to use the orchestrator key or access restricted routes, it receives a 403, and `AccessBoundary` displays an "Insufficient Permissions" shield.

## 8. Authentication Decision
No login or registration is required. We must simply create `frontend/.env` and populate `VITE_API_KEY=test_frontend_key_default`.

## 9. API Client Audit
**CONFIRMED BY SOURCE:** `apiClient.ts` correctly extracts the environment variable and passes it in headers. 

## 10. First-Run UX
The "Access Configuration Required" screen is working exactly as designed, but it should not be seen by judges. It is a symptom of the missing `.env` file.

## 11. Dashboard Audit
**CONFIRMED BY SOURCE:** Components are solid, but **CONTRADICTED BY RUNTIME** because no data loads due to the 401 error.

## 12. Case List Audit
**CONFIRMED BY SOURCE:** Displays cases correctly. **CONTRADICTED BY RUNTIME** because the seed script crashes, leaving the database empty.

## 13. Case Detail Audit
**CONFIRMED BY SOURCE:** The vertical narrative is implemented perfectly. **CONTRADICTED BY RUNTIME** because AI events are never seeded, leaving the AI section blank.

## 14. State UX Audit
**CONFIRMED BY SOURCE:** `UNKNOWN`, `WAITING_APPROVAL`, `SUCCESS`, etc., all map correctly to visual indicators in `RecoveryJourney.tsx` and `StatusBadge.tsx`.

## 15. Human Approval UX
**CONFIRMED BY SOURCE:** Info banner correctly explains the n8n handoff. 

## 16. UNKNOWN UX
**CONFIRMED BY SOURCE:** Alert triangle correctly warns that duplicate execution is blocked.

## 17. AI Behavior Audit
**CLAIMED BUT UNPROVEN:** The previous report claimed AI behavior was validated. In reality, the seed script does not generate AI events (`LLM_RECOMMENDATION_CREATED`), so the frontend displays "No AI recommendation event found". 

## 18. AI Scenario Validation
**NOT VERIFIABLE:** Because the seed script omits AI events, validation cannot be performed in the UI.

## 19. AI Slop Assessment
**CONFIRMED BY SOURCE:** If the LLM keys are missing, the backend falls back to deterministic rules that output generic strings ("Standard recovery procedure"). This risks looking like "AI slop" during a live demo if the real LLM isn't called or if the seed data isn't enriched.

## 20. AI / Policy UX
**CONFIRMED BY SOURCE:** Icons and layout strictly separate Brain (AI) and Shield (Policy).

## 21. Demo Scenario Audit
**CONTRADICTED:** `seed_demo_data.py` attempts to create the 5 scenarios, but it crashes on table cleanup due to FK constraints (`policy_decisions` references `recovery_cases`).

## 22. Seed / API / UI Audit
**CONTRADICTED:** The pipeline fails at the Seed stage. 

## 23. Activity Decision
**CONFIRMED BY SOURCE:** The `/activity` route was correctly hidden.

## 24. System Health Audit
**CONFIRMED BY SOURCE:** Works as expected.

## 25. Loading/Empty/Error UX
**CONFIRMED BY SOURCE:** Handled beautifully via `LoadingSkeleton` and `ErrorState`.

## 26. Responsive Audit
**CONFIRMED BY SOURCE:** Tailwind classes (`md:hidden`, `lg:flex`) correctly degrade the layout for mobile.

## 27. Accessibility Audit
**CONFIRMED BY SOURCE:** Semantic HTML and `prefers-reduced-motion` are present.

## 28. Visual Design Audit
**CONFIRMED BY SOURCE:** Strict adherence to Warm Premium. Beige backgrounds, editorial typography. 

## 29. Warm Premium Preservation Rules
Maintain the existing `#FAFAF7` background. Do not redesign.

## 30. Stitch Continuation Plan
Continue Project ID 1051231661397186252.

## 31. Required Stitch Screens
Following Subagent F analysis, we must generate:
- Access Configuration Required (401 State)
- Unauthorized / Insufficient Permissions (403 State)
- Case Detail — Policy Denial & Suppression (DENIAL)
- Case Detail — Provider Execution Failure (FAILURE)
- Case Detail (Mobile Responsive Variant)

## 32. Detailed Page/State Matrix
| Route | Component | Reachable | Data | Demo Role | Action |
|---|---|---|---|---|---|
| `/` | Dashboard | Yes (401) | None | Overview | Fix .env |
| `/cases` | CaseList | Yes (401) | None | Triage | Fix seed |
| `/cases/:id` | CaseDetail | Yes (401) | None | AI Proof | Fix seed AI events |

## 33. Detailed AI Validation Matrix
| Scenario | Actual Input | Actual Output | Quality | Risk | UI Treatment |
|---|---|---|---|---|---|
| ALL | Missing | "No AI recommendation" | Fails | High | Blank UI |

*Action: Must update seed script to insert `LLM_RECOMMENDATION_CREATED` events.*

## 34. Product Gap Matrix
| Stage | Real? | Evidence | Problem |
|---|---|---|---|
| Seed | No | SQLite IntegrityError | `seed_demo_data.py` crashes on DELETE. |
| API | Yes | 401 Unauthorized | Missing `frontend/.env`. |

## 35. File-Level Implementation Plan
| File | Create/Modify/Delete | Reason | Priority |
|---|---|---|---|
| `frontend/.env` | Create | Resolves the 401 Unauthorized runtime error. | MUST FIX |
| `scripts/seed_demo_data.py` | Modify | Fix FK constraint crash on table DELETE. | MUST FIX |
| `scripts/seed_demo_data.py` | Modify | Insert `LLM_RECOMMENDATION_CREATED` events so Case Detail populates the AI section. | MUST FIX |

## 36. Implementation Sequence
1. Create `frontend/.env` with `VITE_API_KEY`.
2. Generate Stitch screens for DENIAL/FAILURE edge cases.
3. Fix `seed_demo_data.py` table deletion order.
4. Add AI recommendation events to the seed script scenarios.
5. Run full runtime regression.

## 37. Testing Strategy
- **Frontend**: Verify dashboard loads without 401.
- **Runtime**: Verify seed script completes without SQLite errors.
- **AI**: Verify Case Detail displays AI reasoning instead of the "No AI recommendation" fallback.

## 38. Runtime Acceptance
Must prove Dashboard loads, Cases list populates, and Case Detail shows AI data using LIVE RUNTIME.

## 39. Visual Acceptance
Warm Premium identity maintained.

## 40. Demo Acceptance
Judge journey is fully possible from end to end.

## 41. MUST FIX
- Missing `frontend/.env` (causes 401).
- `seed_demo_data.py` SQLite FK crash.
- `seed_demo_data.py` missing AI timeline events.

## 42. SHOULD FIX
- Stitch screens for DENIAL and FAILURE states.

## 43. OPTIONAL
None.

## 44. P20 Handoff
Once the MUST FIX items are implemented, the product will be genuinely ready for P20.

## 45. Stop Conditions
Stop implementation immediately. Do not modify source code. Wait for Gemini implementation.
