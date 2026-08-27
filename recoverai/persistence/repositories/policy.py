import json
from typing import Optional

from recoverai.domain.identifiers import PolicyDecisionId, RecoveryCaseId
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue
from recoverai.persistence.connection import TransactionManager


class PolicyDecisionRepository:
    def __init__(self, connection) -> None:  # type: ignore
        self._conn = connection

    def save(self, decision: PolicyDecision) -> None:
        """
        Saves a PolicyDecision to the database.
        Does NOT execute the decision.
        """
        self._conn.execute(
            """
            INSERT INTO policy_decisions (
                policy_decision_id,
                case_id,
                action_id_or_proposal_id,
                decision,
                policy_version,
                matched_rules_json,
                reason_codes_json,
                evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.policy_decision_id.value,
                decision.case_id.value,
                decision.action_id_or_proposal_id,
                decision.decision.value,
                decision.policy_version,
                json.dumps(decision.matched_rules),
                json.dumps(decision.reason_codes),
                decision.evaluated_at.isoformat(),
            ),
        )

    def get(self, policy_decision_id: PolicyDecisionId) -> Optional[PolicyDecision]:
        row = self._conn.execute(
            "SELECT * FROM policy_decisions WHERE policy_decision_id = ?",
            (policy_decision_id.value,),
        ).fetchone()
        if not row:
            return None

        from datetime import datetime

        return PolicyDecision(
            policy_decision_id=PolicyDecisionId(row["policy_decision_id"]),
            case_id=RecoveryCaseId(row["case_id"]),
            action_id_or_proposal_id=row["action_id_or_proposal_id"],
            decision=PolicyDecisionValue(row["decision"]),
            policy_version=row["policy_version"],
            matched_rules=json.loads(row["matched_rules_json"]),
            reason_codes=json.loads(row["reason_codes_json"]),
            evaluated_at=datetime.fromisoformat(row["evaluated_at"]),
        )
