# Package 04 — Verification

## Pytest (Including Event Ingestion & Persistance Deduplication)

Command: `uv run pytest tests/`

Output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dell\Desktop\RecoverAI
configfile: pyproject.toml
collected 49 items

tests\unit\domain\test_action.py ...                                     [  6%]
tests\unit\domain\test_architecture.py .                                 [  8%]
tests\unit\domain\test_case.py .....                                     [ 18%]
tests\unit\domain\test_event.py .....                                    [ 28%]
tests\unit\domain\test_identifiers.py ....                               [ 36%]
tests\unit\domain\test_misc.py ....                                      [ 44%]
tests\unit\domain\test_money.py ........                                 [ 61%]
tests\unit\ingestion\razorpay\test_normalizer.py ...                     [ 67%]
tests\unit\ingestion\razorpay\test_service.py ..                         [ 71%]
tests\unit\ingestion\razorpay\test_signature.py ....                     [ 79%]
tests\unit\persistence\test_corrupt.py ..                                [ 83%]
tests\unit\persistence\test_persistence.py .....                         [ 93%]
tests\unit\test_foundation.py ...                                        [100%]

============================= 49 passed in 1.46s ==============================
```
*Status: PASS*

## Ruff Linter

Command: `uv run ruff check .`

Output:
```
All checks passed!
```
*Status: PASS*

## Ruff Formatter

Command: `uv run ruff format --check .`

Output:
```
63 files already formatted
```
*Status: PASS*

## Mypy Type Checker

Command: `uv run mypy recoverai/ tests/`

Output:
```
Success: no issues found in 62 source files
```
*Status: PASS*

## Git Architecture Verification

Command: `git diff -- docs/`

Output:
*(Empty output, validating that architecture documents remain unmodified)*
*Status: PASS*

## Git Workspace Verification

Command: `git diff --stat`

Output:
*(Empty output, working tree is clean from existing commits)*
*Status: PASS*

## Supported Event Type Verification

| Razorpay Event | Internal Type | Test |
| --- | --- | --- |
| `payment.authorized` | `PAYMENT_AUTHORIZED` | `test_normalize_supported_events` |
| `payment.captured` | `PAYMENT_CAPTURED` | `test_normalize_supported_events` |
| `payment.failed` | `PAYMENT_FAILED` | `test_normalize_payment_failed` / `test_normalize_supported_events` |
| `payment_link.paid` | `PAYMENT_LINK_PAID` | `test_normalize_supported_events` |
| `payment.downtime.started` | `PAYMENT_DEGRADATION_SIGNAL` | `test_normalize_supported_events` |
| `payment.downtime.updated` | `PAYMENT_DEGRADATION_SIGNAL` | `test_normalize_supported_events` |
