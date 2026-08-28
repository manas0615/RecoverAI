import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AuditActor:
    type: str
    id: str


@dataclass
class AuditEvent:
    event_type: str
    actor: AuditActor
    audit_event_id: str = field(
        default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}"
    )
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    case_id: str | None = None
    action_id: str | None = None
    decision_reference: str | None = None
    policy_version: str | None = None
    previous_state: str | None = None
    new_state: str | None = None
    evidence_references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def redact_secrets(cls, data: dict[str, Any]) -> dict[str, Any]:
        redacted = dict(data)
        sensitive_keys = {
            "api_key",
            "secret",
            "password",
            "token",
            "authorization",
            "card_number",
        }
        for k, v in redacted.items():
            if any(s in k.lower() for s in sensitive_keys):
                redacted[k] = "***REDACTED***"
            elif isinstance(v, dict):
                redacted[k] = cls.redact_secrets(v)
        return redacted

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_event_id": self.audit_event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "actor": {"type": self.actor.type, "id": self.actor.id},
            "case_id": self.case_id,
            "action_id": self.action_id,
            "decision_reference": self.decision_reference,
            "policy_version": self.policy_version,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "evidence_references": self.evidence_references,
            "metadata": self.redact_secrets(self.metadata),
        }
