# PLAN SNAPSHOT SERIALIZATION CORRECTION

**Project:** RecoverAI — Razorpay AI Buildathon 2026 (Track 03: AI Revenue Recovery)  
**Baseline HEAD SHA:** `3d022ce9308acb373f8ecd79eca84df841719623`  
**Execution Date:** August 30, 2026  
**Status:** **PLAN SERIALIZATION CORRECTION VERIFIED**  

---

## 1. Description of Changes

Opaque Python-specific serialization (`pickle` + `base64`) was replaced with explicit, versioned, language-independent `JSON` representation for auditability, portability, and safer persistence.

- **Old Serialization Structure:**
  ```python
  # Opaque Python-pickled binary blob encoded in base64:
  plan_snapshot = base64.b64encode(pickle.dumps(plan)).decode("ascii")
  ```

- **New Serialization Structure:**
  ```python
  # Human-readable versioned JSON string stored directly in SQLite TEXT column:
  plan_snapshot = json.dumps(plan.to_dict())
  ```

- **Schema Version:**
  - Standardized as version `1`.

---

## 2. Affected Files

- [`recoverai/domain/plan.py`](file:///c:/Users/Dell/Desktop/RecoverAI/recoverai/domain/plan.py): Added `to_dict()` and `from_dict()` methods to `InterventionPlan` to safely parse and reconstruct the domain structure.
- [`recoverai/mcp/handlers.py`](file:///c:/Users/Dell/Desktop/RecoverAI/recoverai/mcp/handlers.py): Replaced `pickle.dumps` and `pickle.loads` calls with the new JSON dictionary methods.
- [`tests/integration/test_human_approval.py`](file:///c:/Users/Dell/Desktop/RecoverAI/tests/integration/test_human_approval.py): Updated fixtures to dynamically build and serialize mock plans using `json.dumps(plan.to_dict())`.
- [`tests/unit/domain/test_plan_serialization.py`](file:///c:/Users/Dell/Desktop/RecoverAI/tests/unit/domain/test_plan_serialization.py): Added focused tests verifying round-trip serialization, parameter matching, and validation constraints.

---

## 3. Backward Compatibility & Migration Behavior

For this competition prototype, old pickle snapshots are invalidated. If an old snapshot exists, the parser raises an error (`CORRUPTED_PLAN`) instead of silently deserializing arbitrary pickling content, prompting database recreation or reseeding. This ensures complete runtime memory safety.

---

## 4. Verification & Testing Outcomes

1. **Plan Round-Trip Test:**
   - Validates that action types, confidence scores, reasoning, monetary amounts, and currencies are fully matched.
   - **Status:** **PASSED**

2. **Human Approval Test:**
   - Proves that `intelligence.analyze()` is NOT called to regenerate plans during resumption.
   - **Status:** **PASSED**

3. **Plan-Drift / Financial Safety Verification:**
   - Confirms that the reconstructed plan is re-evaluated by the `PolicyEngine` and cannot bypass high-value ceilings, attempt thresholds, or currency invariants.
   - **Status:** **PASSED**

4. **Consolidated Regression Result:**
   - Pytest Suite: `178 passed`
   - Mypy: `Success: no issues found in 124 source files`
   - Ruff check/format: `Passed (0 errors, 124 files formatted)`
   - Frontend Build: `tsc && vite build` succeeded.
