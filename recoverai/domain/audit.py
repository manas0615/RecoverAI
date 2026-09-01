import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from recoverai.domain.identifiers import (
    EvidenceId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
)


class AuditActorType(str, Enum):
    SYSTEM = "SYSTEM"
    ML_MODEL = "ML_MODEL"
    LLM_AGENT = "LLM_AGENT"
    POLICY_ENGINE = "POLICY_ENGINE"
    MCP_TOOL = "MCP_TOOL"
    N8N_WORKFLOW = "N8N_WORKFLOW"
    RAZORPAY = "RAZORPAY"
    HUMAN = "HUMAN"
    SIMULATOR = "SIMULATOR"
    VERIFICATION = "VERIFICATION"
    STATE_MACHINE = "STATE_MACHINE"


class AuditEventType(str, Enum):
    CASE_CREATED = "CASE_CREATED"
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    RISK_ASSESSMENT_CREATED = "RISK_ASSESSMENT_CREATED"
    CAUSE_ASSESSMENT_CREATED = "CAUSE_ASSESSMENT_CREATED"
    INTERVENTION_PROPOSED = "INTERVENTION_PROPOSED"
    POLICY_DECISION_CREATED = "POLICY_DECISION_CREATED"
    ACTION_AUTHORIZED = "ACTION_AUTHORIZED"
    ACTION_EXECUTING = "ACTION_EXECUTING"
    ACTION_EXECUTION_UNKNOWN = "ACTION_EXECUTION_UNKNOWN"
    RAZORPAY_REQUEST_COMPLETED = "RAZORPAY_REQUEST_COMPLETED"
    VERIFICATION_STARTED = "VERIFICATION_STARTED"
    VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
    RECOVERY_CONFIRMED = "RECOVERY_CONFIRMED"
    RECOVERY_SUPPRESSED = "RECOVERY_SUPPRESSED"
    CASE_ESCALATED = "CASE_ESCALATED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_TRIGGER_FAILED = "WORKFLOW_TRIGGER_FAILED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"
    WEBHOOK_DUPLICATE = "WEBHOOK_DUPLICATE"
    WEBHOOK_REJECTED = "WEBHOOK_REJECTED"
    WEBHOOK_SIGNATURE_REJECTED = "WEBHOOK_SIGNATURE_REJECTED"
    RECOVERY_STATE_CHANGED = "RECOVERY_STATE_CHANGED"
    LLM_RECOMMENDATION_CREATED = "LLM_RECOMMENDATION_CREATED"


@dataclass
class AuditActor:
    type: AuditActorType
    id: str


@dataclass
class AuditEvent:
    event_type: AuditEventType
    actor: AuditActor
    audit_event_id: str = field(
        default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}"
    )
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    case_id: RecoveryCaseId | None = None
    action_id: RecoveryActionId | None = None
    decision_reference: PolicyDecisionId | None = None
    policy_version: str | None = None
    previous_state: str | None = None
    new_state: str | None = None
    evidence_references: list[EvidenceId] = field(default_factory=list)
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
            "credentials",
            "encryption_key",
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
            "event_type": self.event_type.value,
            "actor": {"type": self.actor.type.value, "id": self.actor.id},
            "case_id": str(self.case_id) if self.case_id else None,
            "action_id": str(self.action_id) if self.action_id else None,
            "decision_reference": str(self.decision_reference)
            if self.decision_reference
            else None,
            "policy_version": self.policy_version,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "evidence_references": [str(e) for e in self.evidence_references],
            "metadata": self.redact_secrets(self.metadata),
        }
