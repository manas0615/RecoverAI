# Package 16 — User Walkthrough

## The Real User Journey

The RecoverAI frontend is designed to support the primary operational journey of an analyst or manager tracking revenue recovery efforts.

### 1. Dashboard Overview
When the user arrives at `/`, they are presented with a high-level overview.
- **Hero Metrics:** The user immediately sees the total "Open Revenue at Risk" (aggregated from all `OPEN` cases in the API) and the number of "Active Cases." Since P15 does not provide a verified recovered revenue total or recovery rate, these metrics are shown in a muted, graceful "Data Unavailable" state rather than fabricating data.
- **Attention Pipeline:** An "Open Recovery Cases" summary clearly states how many cases are currently flowing through the pipeline.
- **System Health:** A unified "System Operational" badge confirms backend connectivity.
- **Recent Cases:** A table lists recent cases. The user can click any row to drill down.

### 2. Case Detail Drilldown
Clicking a case navigates to `/cases/:id`. This is the product-defining experience.
- **Hero:** The amount at risk is displayed prominently in a large display font, alongside the current workflow status pill (e.g., `WAITING_APPROVAL`).
- **Recovery Journey Stepper:** A horizontal timeline visually indicates how far the case has progressed (`DETECTED → ASSESSED → POLICY → EXECUTING → VERIFYING`).
- **Decision Transparency:** The layout uses editorial columns to clearly separate the AI Recommendation from the determinist Policy Decision. These are populated directly by parsing the timeline events (`LLM_RECOMMENDATION_CREATED` and `POLICY_DECISION_CREATED`).
- **Workflow Handoff:** If the case requires human approval, a prominent notice explains that approval and execution are managed externally via n8n (no fake "Execute" buttons exist).

### 3. Full Audit Transparency
At the bottom of the Case Detail page, the full Audit Timeline is displayed. Every event is shown with its actor (System, ML Model, Policy Engine), timestamp, and any relevant state transitions or metadata, providing absolute transparency into how decisions were made.
