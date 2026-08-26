# Package 06 — Revenue Intelligence Verification

## Risk Assessment Tests
Verified via `test_deterministic_analyzer_customer` and `test_deterministic_analyzer_systemic`. Tests assert `RiskAssessment` object instantiation, model name binding to `deterministic_baseline`, and heuristic probability boundaries matching the extracted context features (e.g. `0.8` vs `0.1`). These are baseline heuristic outputs, not calibrated probabilities.

## Cause Assessment Tests
Verified via `test_deterministic_analyzer_systemic` which asserts a `SYSTEMIC_DEGRADATION` category, and `test_mock_llm_analyzer_success` which proves the mock gateway returns `MOCK_CATEGORY` bound to an `AnalysisType.LLM`.

## Intervention Tests
Verified via `test_deterministic_analyzer_customer`. Tests assert that the candidate list is generated, ranked by expected value, and the optimal action (e.g., `ActionType.CREATE_PAYMENT_LINK`) is bound to `selected_action_type`.

## Evidence Grounding Tests
Verified via `test_deterministic_analyzer_customer`. Asserts that `len(cause.evidence_references) == 1` and `cause.evidence_references[0].source_id == "evt_1"`, linking the analysis directly to the `RevenueEvent`. Furthermore, `test_evidence_reference_validation` ensures that hallucinated evidence (not present in the input context) is explicitly stripped out by the orchestrator.

## Model Output Validation
The `LLMGateway` strictly defines `-> CauseAssessment` and `-> list[InterventionCandidate]`. The Python type-checker enforces these boundaries (0 type-checking errors).

## AI Failure Tests
Verified via `test_mock_llm_analyzer_cause_fallback` and `test_mock_llm_analyzer_candidates_fallback`. Tests prove that a raised exception in the LLM Gateway triggers the fallback logic natively, preserving `AnalysisType.RULE_BASED`.

## Prompt/Data Boundary Tests
Customer text and payload structures are isolated inside `RevenueEvent.metadata`. The `LLMGateway` signature passes this explicitly as context, isolating raw data from execution intents. Verified via `test_prompt_data_boundary_safety` which proves malicious metadata ("Ignore previous instructions...") does not leak into instruction parsing.

## Policy Separation Tests
The tests prove that `RevenueIntelligenceAnalyzer` returns an `InterventionPlan`. It does not import `PolicyDecisionId`, nor does it mutate the `RecoveryCase` state.

## Persistence Tests
Persistence mapping relies on existing P03 boundaries. No schema modifications were implemented. 

## Regression Tests
```text
$ uv run pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dell\Desktop\RecoverAI
configfile: pyproject.toml
collected 73 items

tests\unit\domain\test_action.py ...                                     [  4%]
tests\unit\domain\test_architecture.py .                                 [  5%]
tests\unit\domain\test_case.py .....                                     [ 12%]
tests\unit\domain\test_event.py .....                                    [ 19%]
tests\unit\domain\test_identifiers.py ....                               [ 24%]
tests\unit\domain\test_misc.py ....                                      [ 30%]
tests\unit\domain\test_money.py ........                                 [ 41%]
tests\unit\ingestion\razorpay\test_normalizer.py ........                [ 52%]
tests\unit\ingestion\razorpay\test_service.py ..                         [ 54%]
tests\unit\ingestion\razorpay\test_signature.py ....                     [ 60%]
tests\unit\intelligence\test_analyzer.py .......                         [ 69%]
tests\unit\persistence\test_corrupt.py ..                                [ 72%]
tests\unit\persistence\test_migration_002.py ...                         [ 76%]
tests\unit\persistence\test_persistence.py .....                         [ 83%]
tests\unit\persistence\test_version.py ...                               [ 87%]
tests\unit\state_machine\test_engine.py ......                           [ 95%]
tests\unit\test_foundation.py ...                                        [100%]

============================= 73 passed in 2.87s ==============================
```

```text
$ uv run ruff format --check .
76 files already formatted
```

```text
$ uv run ruff check .
All checks passed!
```

```text
$ uv run mypy recoverai/ tests/
Success: no issues found in 73 source files
```
