# Pre-P20 Product / UX / AI Behavior Validation & Improvement Plan

## 1. Executive Summary
This document outlines the final product-level validation and improvement plan for RecoverAI prior to Package 20 (Demo & Submission Build). The audit expands beyond backend correctness to ensure product completeness, UX storytelling, AI quality, and visual polish. The canonical Warm Premium UI will be preserved. A central requirement before P20 is the explicit validation of actual AI behavior and the clear visual separation of AI recommendations from deterministic policy decisions.

## 2. Current Product Reality & Original Product Intent
RecoverAI is a secure, intelligent operational dashboard. It detects payment failures, uses LLMs to recommend interventions, applies deterministic policies, orchestrates actions via n8n, and verifies outcomes. The frontend currently pulls live data via the P15 REST API. `seed_demo_data.py` accurately generates coherent test cases. 

## 3. Product Completeness Audit
The product completeness extends beyond route existence to encompass all critical lifecycle and operational states:
- **Dashboard**: User goal is global oversight. Requires loading/empty states.
- **Recovery Cases**: User goal is triage. Sorting/filtering/search should only be added when it uses fields already available through P15, materially improves the merchant/judge workflow, does not require invented APIs, and does not duplicate backend business logic. Do not turn the Cases page into an analytics platform.
- **Case Detail**: User goal is deep investigation and narrative understanding.
- **System Health**: User goal is operational confidence.
- **Activity**: Currently a placeholder. Must be removed from primary navigation to avoid an unfinished "Coming Soon" experience.
- **Edge States (401/403/404/500/Unavailable)**: Requires graceful access UX, not raw errors.

## 4. Case Detail UX Narrative
Case Detail is the primary product experience. The page must communicate a clear narrative:
`WHY DID THIS CASE HAPPEN?`
↓
`WHAT DID AI UNDERSTAND?`
↓
`WHAT DID AI RECOMMEND?`
↓
`WHAT DID POLICY DECIDE?`
↓
`WHAT DID THE SYSTEM DO?`
↓
`WHAT VERIFIED THE OUTCOME?`
↓
`WHAT HAPPENS NEXT?`

The UI must explicitly and visually communicate:
**AI SUGGESTS**
↓
**POLICY DECIDES**
↓
**SYSTEM EXECUTES**
↓
**VERIFICATION PROVES**

*UX Requirement:* Keep AI and Policy visually independent. AI recommendations MUST NOT be visually or semantically presented as authorization.

## 5. Human Approval UX
The UI/workflow experience must communicate:
`WAITING_APPROVAL` → human input → backend state re-check → PolicyEngine re-evaluation → `APPROVE` only → authorized execution.
Human approval is not itself financial authorization; the UI must reflect this separation.

## 6. UNKNOWN Safety Visibility
The UI must make clear:
`EXECUTION_UNKNOWN` ≠ `SUCCESS` ≠ `FAILURE`
`EXECUTION_UNKNOWN` → reconciliation only → no blind financial retry.
The user must understand that the system is paused for external state reconciliation.

## 7. First-Run / Access UX (401 vs 403)
**NO LOGIN / REGISTRATION IS REQUIRED.**
- `VITE_API_KEY` → `FRONTEND_API_KEY`
- **401 (Authentication/Configuration Problem)**: The Access Configuration state should explain that the frontend could not authenticate with the backend, instruct the user to check that `VITE_API_KEY` corresponds to `FRONTEND_API_KEY`, and prompt them to restart the frontend after configuration. Do NOT display secret values.
- **403 (Authenticated but Insufficient Permissions)**: Distinct UX treatment indicating insufficient permissions. Do not conflate 401 and 403.

## 8. Real AI Behavior Validation
AI behavior cannot be classified as verified merely because the LLM Gateway returns structured JSON. Actual representative RecoveryCase AI results must be actively examined. We must NOT accept merely schema validity, successful API calls, or the existence of a field.

Validation MUST examine actual application outputs across at least:
A. Straightforward payment failure
B. High-value/sensitive case
C. Systemic degradation
D. EXECUTION_UNKNOWN
E. POLICY DENIAL/SUPPRESS
F. HUMAN ESCALATION

*Criteria:* Assessment must ensure case specificity, recommendation relevance, evidence grounding, meaningful response variation, financial safety, clarity, absence of unsupported claims, and absence of generic AI-slop.

## 9. Do Not Force AI Outputs
The implementation/validation plan explicitly prohibits hardcoding or prompting the model toward a desired demo answer merely to satisfy a UI scenario. Scenario labels are test contexts; expected AI behavior is a validation hypothesis; actual P06/P10 output must be observed. Do not hardcode "High-value always means escalation" unless explicitly produced by the existing architecture.

Required flow:
`actual seeded RecoveryCase` → `actual P06/P10 intelligence` → `observe actual AI output` → `evaluate relevance/safety/evidence` → `display actual result` → `P07 independently decides`.
The demo scenario must be selected based on the actual resulting system behavior, not by fabricating an AI response.

## 10. Visual Quality & CSS Rules
The current beige/cream implementation remains the baseline. Evaluate hierarchy, whitespace, card density, typography, and state communication to ensure the result resembles a professional SaaS product.
*CSS Rule:* "The Warm Premium visual identity, palette, typography direction, surface language, and overall design system are frozen. Any CSS/token changes must be narrowly justified as UX improvements that preserve the same design system."

## 11. Responsive Requirement
Verify actual UX on Desktop, Tablet, and Mobile.
Especially evaluate: Case Detail, timeline, AI/Policy comparison, UNKNOWN state, WAITING_APPROVAL state, navigation drawer, and Cases list. Do not merely inspect CSS breakpoints.

## 12. Stitch Continuity Plan
- **Stitch Project ID**: `1051231661397186252`
- **Design System Asset**: `assets/15122457507156157995`
- Never create another Stitch project, design system, or return to dark navy.
- Stitch is a design reference tool, not an authority replacing the canonical React implementation. (Do not invoke Stitch during this planning task).

## 13. Final Demo Scenario Matrix
| Scenario | Seeded Backend Data | P15 Response | P16 Rendering | AI Behavior | Policy Behavior | Execution State | Verification State | User Explanation / Next Steps |
|---|---|---|---|---|---|---|---|---|
| **SUCCESS** | Complete | Valid | Full Narrative | Observed Result | Approves | Success | Verified | Recovery successful. |
| **FAILURE** | Complete | Valid | Clear Error | Observed Result | Approves | Failed | Failed | Recovery attempt failed or was not successfully verified; the case remains available for appropriate follow-up according to its authoritative state. |
| **EXECUTION_UNKNOWN**| Complete | Valid | Warning UI | Observed Result | Approves | Unknown | Pending | External execution state is uncertain. Reconciliation only; no new financial action is attempted automatically. |
| **POLICY_DENIAL** | Complete | Valid | Blocked UI | Observed Result | Denies | None | None | Blocked by systemic rules. |
| **HUMAN_ESCALATION**| Complete | Valid | Paused UI | Observed Result | Escalates | Paused | None | Waiting for human approval via n8n. |

## 14. Final AI Quality Matrix
| Scenario | Hypothesis to Evaluate | Actual Data Available | Validation | UX Presentation |
|---|---|---|---|---|
| Basic Failure | Recommend payment link | Event/Case Data | Observe actual response | Distinct AI Card |
| High-Value | Recommend escalation | Case context | Observe actual response | High severity visual |
| Unknown State | No blind retry | Timeline | Observe actual response | Blocked recommendation |

## 15. Final Page/State Matrix
| Route/State | Current Quality | Required Quality | Demo Critical | Action |
|---|---|---|---|---|
| Dashboard | Good | Polished metrics | YES | Refine spacing/figures |
| Cases | Good | Triage capability | YES | Ensure clear sorting/filters |
| Case Detail | Functional | Narrative Flow | YES | Decouple AI/Policy visually |
| Activity | Placeholder | Remove | NO | Remove from primary nav |
| 401 Error | Console | Graceful UI | YES | Build Access Configuration UX |
| 403 Error | Console | Graceful UI | YES | Build Unauthorized UX |
| SUCCESS | Good | Premium | YES | Emphasize verification |
| UNKNOWN | Warning | Clear limits | YES | Explicit "Reconciliation Only" |

## 16. Final Priority Matrix
### MUST FIX BEFORE P20
- 401/403 graceful access UX
- Case Detail AI → Policy narrative (explicitly communicating AI Suggests → Policy Decides)
- UNKNOWN clarity (reconciliation only)
- WAITING_APPROVAL clarity
- Remove/hide unfinished Activity experience
- Actual AI behavior validation against representative cases (no AI slop, no forcing outputs)

### SHOULD FIX BEFORE P20
- Responsive polish
- Cases triage improvements
- Loading/empty/error refinements where materially useful

### OPTIONAL
- Subtle motion/timeline polish

## 17. Final Acceptance Criteria
- No login/registration is incorrectly added.
- No new auth system or Stitch project is created.
- 401/403 handled clearly (401 = config problem, 403 = insufficient permissions).
- Warm Premium identity preserved.
- Case Detail tells the explicit AI SUGGESTS → POLICY DECIDES → SYSTEM EXECUTES → VERIFICATION PROVES story.
- Representative cases produce meaningful AI behavior evaluated as validation hypotheses against observed output, not forced outputs.
- AI recommendations are never presented as authorization.
- UNKNOWN is clearly reconciliation-only. No automatic financial retry is implied.
- Human approval is decoupled from policy authority.
- Seeded scenarios flow P15 -> P16 correctly without fabricated data.
- Demo-critical states (loading/empty/error) are professional.
- Responsive layouts work across breakpoints.
- The 3-5 minute judge journey is executable on real data.

## 18. Stop Conditions
Stop. Do not implement frontend, backend, or workflows. Do not invoke Stitch. Do not start P20.
