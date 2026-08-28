# Package 13 Walkthrough

## How the Audit Layer Works
The Audit domain acts as a standalone observer. It intercepts business decisions without affecting the domain models. 

1. **Instantiation**: The system constructs an AuditActor defining who made the decision (e.g., LLM_AGENT, POLICY_ENGINE, N8N_WORKFLOW).
2. **Construction**: An AuditEvent is generated utilizing strong correlation identifiers. This spans tracking policy_version, decision_reference, and cross-referencing previous and current states (previous_state -> 
ew_state).
3. **Redaction Check**: The AuditEvent.redact_secrets() is invoked implicitly during object serialization. This guarantees credentials embedded inside metadata (e.g., failed API attempts) are wiped (***REDACTED***).
4. **Append**: The event is injected into the database using AuditRepository.append(event). If the transaction succeeds, the append stays. If a database error occurs later in the process flow, the unified TransactionManager correctly rolls back both the business payload and the audit log, preventing drift.
