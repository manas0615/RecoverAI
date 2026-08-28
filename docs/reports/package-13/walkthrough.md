# Package 13 Walkthrough

## How the Audit Layer Works
The Audit implementation is strictly integrated into the business transaction boundaries to guarantee atomic persistency. It is not an async "standalone observer" that might lose data; it is an explicit synchronous requirement.

1. **Instantiation**: The system constructs an AuditActor defining who made the decision (e.g., LLM_AGENT, POLICY_ENGINE, N8N_WORKFLOW) using the strict AuditActorType enum.
2. **Construction**: An AuditEvent is generated utilizing strong correlation identifiers. This spans tracking policy_version, decision_reference, and cross-referencing previous and current states (previous_state -> 
ew_state). All events use the controlled AuditEventType vocabulary.
3. **Redaction Check**: The AuditEvent.redact_secrets() is invoked implicitly during object serialization. This guarantees credentials embedded inside metadata (e.g., failed API attempts) are wiped (***REDACTED***).
4. **Append**: The event is injected into the database using AuditRepository.append(event). Since it uses the same sqlite3.Connection as the overarching TransactionManager, an audit write failure successfully fails the entire business mutation, preventing ghost state drift.
