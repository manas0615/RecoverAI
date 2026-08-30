# RECOVERAI — P22 POST-IMPLEMENTATION FORENSIC AUDIT
## CRITICAL BLANK CASE DETAIL ROUTE

### Executive Summary
The completely blank white page observed when navigating to `/cases/case_LIVE` is caused by an unhandled React runtime exception in `CaseDetailView.tsx`. The regression **did not originate in P22**; it is a latent bug in the Evidence section (added in P21) that only surfaces when a case contains events without a financial amount.

Additionally, a separate P22 regression was discovered in the backend `analyze_case` endpoint which will cause a 500 Internal Server Error when analyzing a case that lacks an intervention plan.

### 1. Root Cause: Frontend Blank Page (React Runtime Exception)
**Location:** `frontend/src/pages/CaseDetailView.tsx` (Evidence Section)

The `case_LIVE` scenario is intentionally different from fully seeded historical cases and may contain events that do not have an associated financial amount (e.g., system events or API errors). 

When the backend serializes these events in `GET /recovery-cases/{case_id}`, it sets `currency` to `null` if the event lacks an amount:
```python
"currency": e.amount.currency.value if e.amount else None,
```

In `CaseDetailView.tsx`, the Evidence section maps over `caseData.events` and unconditionally attempts to format the amount:
```tsx
{(ev.amount_minor / 100).toLocaleString(undefined, { style: 'currency', currency: ev.currency })}
```

When `ev.currency` is `null`, `toLocaleString` throws a fatal error:
`RangeError: Invalid currency code : null` (or `TypeError` depending on the JS engine).

Because `CaseDetailView` is not wrapped in a React `<ErrorBoundary>`, this uncaught exception bubbles up to the root, unmounting the entire component tree and resulting in the observed **completely blank white page**.

### 2. Secondary Root Cause: Backend P22 Regression
**Location:** `recoverai/api/main.py` (`analyze_case` endpoint)

While investigating the frontend, a P22 regression was discovered in the backend that will fail if the `case_LIVE` scenario is analyzed before an intervention plan is formed.

P22 modified the `metadata` dictionary creation to include `expected_recovery_amount`:
```python
"expected_recovery_amount": plan.expected_recovery_value.amount_minor
if plan.expected_recovery_value
else (
    risk.expected_recovery_value.amount_minor
    if risk.expected_recovery_value
    else 0
),
```

If `plan` is `None` (which is a valid state before or during early analysis), accessing `plan.expected_recovery_value` throws an `AttributeError: 'NoneType' object has no attribute 'expected_recovery_value'`. This will cause the `POST /recovery-cases/{case_id}/analyze` endpoint to return a 500 error.

### Conclusion
- **Did the blank page regression come from P22?** No. The blank page is caused by the Evidence section's lack of a `null` check on `ev.currency`, which was present before P22.
- **Are there any P22 regressions?** Yes. The backend `analyze_case` endpoint introduced an `AttributeError` risk when `plan` or `cause` are `None`.

No fixes have been applied yet per the ZERO-CHANGE directive. The application requires these null-safety checks to be implemented in both the frontend and backend.
