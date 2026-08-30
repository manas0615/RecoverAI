import re

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

# CORRECTION #1: Verification Architecture
old_verif = """```mermaid
graph TD
    RZ[Razorpay] -->|payment_link.paid| WH[Webhook Endpoint]
    WH --> HMAC[HMAC Verification]
    HMAC --> NORM[Event Normalization]
    NORM --> CORR[Provider Correlation]
    CORR --> VE[P09 VerificationEngine]
    VE --> VAL[Amount + Currency + Ref Validation]
    VAL -->|Match| SUCC[VERIFIED_SUCCESS]
    VAL -->|Mismatch| FAIL[Log Security Alert]
```
*Invalid HMACs, mismatched amounts, incorrect currencies, or duplicate webhooks are safely trapped and logged.*"""

new_verif = """```mermaid
graph TD
    RZ[Razorpay] -->|payment_link.paid| WH[Webhook Endpoint]
    WH --> HMAC[HMAC Verification]
    HMAC --> NORM[Event Normalization]
    NORM --> CORR[Provider Correlation]
    CORR --> VE[VerificationEngine P09]
    VE --> VAL[Amount + Currency + Reference Validation]
    VAL -->|Match| SUCC[VERIFIED_SUCCESS]
    VAL -->|Mismatch| FAIL[UNKNOWN / VERIFICATION NOT CONFIRMED]
    FAIL --> NOREC[NO RECOVERY CLAIM]
```
*A mismatch does not equal a verified recovery; the system fails conservatively, ensuring no false claims are made.*"""

readme = readme.replace(old_verif, new_verif)

# CORRECTION #2: Recovery Lifecycle AI/Fallback
old_lifecycle = """```mermaid
stateDiagram-v2
    [*] --> DETECT: Webhook / API
    DETECT --> EVIDENCE: Gather Context
    EVIDENCE --> ANALYZE: Gemini
    ANALYZE --> POLICY: Recommend Action
    
    state POLICY {
        direction LR
        Evaluate --> DENY
        Evaluate --> ESCALATE
        Evaluate --> APPROVE
    }
    
    DENY --> STOP: No Action Taken
    ESCALATE --> HUMAN_APPROVAL: Wait for Agent
    APPROVE --> EXECUTE: RecoveryActionService
    
    EXECUTE --> VERIFY: Wait for Provider Event
    VERIFY --> RECOVERED: Match payment_link.paid
    
    RECOVERED --> AUDIT
    STOP --> AUDIT
    HUMAN_APPROVAL --> AUDIT
```
*Important lifecycle transitions are recorded in the audit timeline, with technical evidence available where applicable.*"""

new_lifecycle = """```mermaid
stateDiagram-v2
    [*] --> DETECT: Webhook / API
    DETECT --> EVIDENCE: Gather Context
    
    state ANALYZE {
        direction LR
        Gemini
        Deterministic_Fallback
    }
    EVIDENCE --> ANALYZE: Revenue Intelligence
    ANALYZE --> POLICY: Recommend Action
    
    state POLICY {
        direction LR
        Evaluate --> DENY
        Evaluate --> ESCALATE
        Evaluate --> APPROVE
    }
    
    DENY --> STOP: No Action Taken
    ESCALATE --> HUMAN_APPROVAL: Wait for Agent
    APPROVE --> EXECUTE: RecoveryActionService
    
    EXECUTE --> VERIFY: Wait for Provider Event
    VERIFY --> RECOVERED: Match payment_link.paid
    
    RECOVERED --> AUDIT
    STOP --> AUDIT
    HUMAN_APPROVAL --> AUDIT
```
*Gemini is used when configured and available. The application has a deterministic fallback when the provider is unavailable or the output cannot be safely validated.*"""

readme = readme.replace(old_lifecycle, new_lifecycle)

# Terminology: VerificationEngine (P09)
readme = readme.replace("P09 VerificationEngine", "VerificationEngine (P09)")
readme = readme.replace("P09 Webhook verification engine", "VerificationEngine (P09)")

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

# Update the report
report_path = "docs/reports/package-26a/p26a_correction_and_freeze.md"
with open(report_path, "r", encoding="utf-8") as f:
    report = f.read()

new_report = report.replace(
    "## Corrections Made",
    "## Corrections Made\n- **Verification Architecture Diagram:** Corrected to show a conservative UNKNOWN failure path (NO RECOVERY CLAIM) instead of just a generic security alert.\n- **Recovery Lifecycle Diagram:** Updated the analysis stage to accurately branch between Gemini and Deterministic Fallback, avoiding the implication that Gemini handles 100% of cases.\n- **Terminology:** Standardized references to `VerificationEngine (P09)`."
)
with open(report_path, "w", encoding="utf-8") as f:
    f.write(new_report)

