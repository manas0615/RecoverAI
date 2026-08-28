# Package 16 — User Walkthrough

## The Real User Journey

The RecoverAI frontend is designed to support the primary operational journey of an analyst or manager tracking revenue recovery efforts across all devices (Desktop, Tablet, Mobile).

### 1. Dashboard Overview
When the user arrives at `/`, they are presented with a high-level overview.
- **Hero Metrics:** The user immediately sees the total "Open Revenue at Risk" (aggregated from all `OPEN` cases in the API) and the number of "Active Cases." Since P15 does not provide a verified recovered revenue total or recovery rate, these metrics are shown in a muted, graceful "Data Unavailable" state rather than fabricating data.
- **Attention Pipeline:** An "Open Recovery Cases" summary clearly states how many cases are currently flowing through the pipeline.
- **System Health:** A unified "System Operational" badge confirms backend connectivity.
- **Recent Cases:** A fully responsive table lists recent cases. On mobile, this gracefully transforms into a vertical stack of touch-friendly compact cards.

### 2. Recovery Cases List
Navigating to `/cases` provides a full-width list view of all detected cases. Like the Dashboard, this view fully adapts to mobile contexts, ensuring that analysts can monitor the entire pipeline from any device.

### 3. Case Detail & Lifecycle Tracking
Clicking a case navigates to `/cases/:id`. This is the product-defining experience, capable of rendering the *entire* recovery lifecycle.
- **Hero:** The amount at risk is displayed prominently in a large display font, alongside the current workflow status pill (e.g., `WAITING_APPROVAL`, `VERIFIED_SUCCESS`).
- **Recovery Journey Stepper:** A horizontal timeline visually indicates how far the case has progressed (`DETECTED → ASSESSED → POLICY → EXECUTING → VERIFYING`). It provides specific visual indicators for terminal success, failure, or unknown execution states.
- **Decision Transparency:** The layout uses editorial columns to clearly separate the AI Recommendation from the deterministic Policy Decision.
- **Workflow Handoffs:** For states like `WAITING_APPROVAL` or `ESCALATED`, a prominent "Human Intervention Required" notice explains that approval and execution orchestration are managed externally via n8n.
- **Unknown States:** If an execution state times out, a stark warning clearly informs the analyst that the external provider's state is `UNKNOWN` and automatic execution is paused.

### 4. Full Audit Transparency & System Health
At the bottom of the Case Detail page, the full Audit Timeline is displayed. Every event is shown with its actor (System, ML Model, Policy Engine), timestamp, and relevant state transitions. 

By utilizing the navigation sidebar, the user can now also reach:
- **System Health:** A dashboard reflecting real-time connectivity status against the backend (powered purely by `GET /api/health`).
- **Activity Log:** A global polished "Coming Soon" placeholder that visually prepares the application for a future centralized audit stream (slated for Package 18), maintaining transparency without fabricating data.
