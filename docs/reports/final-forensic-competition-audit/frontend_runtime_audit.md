# 8. Frontend Runtime Audit

**Status:** Visually Polished but Operationally Brittle.

## 1. Error Swallowing
`frontend/src/api/client.ts` uses `response.statusText` on failures and drops the actual JSON error body (`response.json()`) returned by FastAPI. This means backend policy rejections, LLM rate limits, and validation errors are uniformly presented as generic "API Error" or "Analysis unavailable" states to the user.

## 2. Hardcoded Cosmetic Statuses
- **Test Mode Badge:** `TestModeBadge.tsx` is statically rendered in the AppShell, completely detached from backend configuration.
- **Recovery Rate:** Hardcoded to use `UnavailableMetric`.
- **System Health:** Hardcoded to always display "RecoverAI backend is reachable and responding normally."

## 3. Client-Side Analytics Bypassing
Despite a dedicated `GET /analytics` endpoint returning `revenue_at_risk`, `verified_recovered`, and `active_cases`, `Dashboard.tsx` manually recalculates these metrics using client-side `.reduce` functions over the `useCases()` list, breaking backend state authority.

## 4. Accessibility Violations
- Unlabeled interactive elements (e.g. Back button in `CaseDetailView`).
- `FunnelChart` and `RecoveryJourney` stepper lack ARIA attributes, meaning progress is invisible to screen readers.
- Low contrast text (`--color-text-muted`) fails WCAG AA standards.

**Verdict:** The UI is gorgeous and fulfills the demo requirement visually, but it is heavily mocked and brittle. A judge inspecting the network tab or React components will quickly spot the disconnected logic.
