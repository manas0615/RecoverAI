import sqlite3

from recoverai.domain import (
    ActionStatus,
    ActionType,
    PolicyDecisionId,
    RecoveryAction,
    RecoveryActionId,
    RecoveryCaseId,
)
from recoverai.persistence.exceptions import DuplicateEntityError
from recoverai.persistence.mappers import dt_to_str, str_to_dt


class RecoveryActionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, action: RecoveryAction) -> None:
        """
        Upserts RecoveryAction.
        Handles optimistic concurrency on UPDATE by requiring the status to match
        what we expect or by just blindly updating if we don't pass an old_status.
        To be strictly safe against race conditions during state transitions:
        If the row exists, we update. If it's a new state transition (e.g., executing),
        the caller must ensure it hasn't already been transitioned by another worker.
        Here we do a simple overwrite, but the `ConcurrencyError` is raised if
        we want to enforce conditional updates. We will provide a specific conditional update
        method if needed by P05, but `save` will just synchronize state.
        Wait, for P03 requirement: "concurrency... exactly one successful creation/update".
        The unique index on (case_id, action_type, attempt_number) prevents duplicate attempts.
        The unique index on (idempotency_key) prevents duplicate logical executions.
        """
        cur = self.conn.execute(
            "SELECT status FROM recovery_actions WHERE action_id = ?",
            (action.action_id.value,),
        )
        existing = cur.fetchone()

        try:
            if existing:
                # Update
                # For safety, we could ensure that we are not reverting a terminal state,
                # but domain logic protects against that in Python. We just sync.
                self.conn.execute(
                    """
                    UPDATE recovery_actions SET
                        policy_decision_id = ?,
                        idempotency_key = ?,
                        workflow_execution_reference = ?,
                        external_reference = ?,
                        attempt_number = ?,
                        status = ?,
                        failure_reason = ?,
                        started_at = ?,
                        completed_at = ?
                    WHERE action_id = ?
                """,
                    (
                        action.policy_decision_id.value
                        if action.policy_decision_id
                        else None,
                        action.idempotency_key,
                        action.workflow_execution_reference,
                        action.external_reference,
                        action.attempt_number,
                        action.status.value,
                        action.failure_reason,
                        dt_to_str(action.started_at),
                        dt_to_str(action.completed_at),
                        action.action_id.value,
                    ),
                )
            else:
                self.conn.execute(
                    """
                    INSERT INTO recovery_actions (
                        action_id, case_id, action_type, policy_decision_id,
                        idempotency_key, workflow_execution_reference,
                        external_reference, attempt_number, status, failure_reason,
                        requested_at, started_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        action.action_id.value,
                        action.case_id.value,
                        action.action_type.value,
                        action.policy_decision_id.value
                        if action.policy_decision_id
                        else None,
                        action.idempotency_key,
                        action.workflow_execution_reference,
                        action.external_reference,
                        action.attempt_number,
                        action.status.value,
                        action.failure_reason,
                        dt_to_str(action.requested_at),
                        dt_to_str(action.started_at),
                        dt_to_str(action.completed_at),
                    ),
                )
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateEntityError(f"Duplicate action / constraint failed: {e}")
            raise

    def get(self, action_id: RecoveryActionId) -> RecoveryAction | None:
        cur = self.conn.execute(
            "SELECT * FROM recovery_actions WHERE action_id = ?", (action_id.value,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return self._map_row(row)

    def get_pending_verification(self, case_id: RecoveryCaseId) -> list[RecoveryAction]:
        cur = self.conn.execute(
            "SELECT * FROM recovery_actions WHERE case_id = ? AND status IN ('VERIFICATION_PENDING', 'EXECUTION_UNKNOWN')",
            (case_id.value,),
        )
        return [self._map_row(dict(row)) for row in cur.fetchall()]

    def get_by_case(self, case_id: RecoveryCaseId) -> list[RecoveryAction]:
        cur = self.conn.execute(
            "SELECT * FROM recovery_actions WHERE case_id = ?", (case_id.value,)
        )
        return [self._map_row(dict(row)) for row in cur.fetchall()]

    def _map_row(self, row: dict) -> RecoveryAction:
        return RecoveryAction(
            action_id=RecoveryActionId(row["action_id"]),
            case_id=RecoveryCaseId(row["case_id"]),
            action_type=ActionType(row["action_type"]),
            requested_at=str_to_dt(row["requested_at"]),  # type: ignore
            policy_decision_id=PolicyDecisionId(row["policy_decision_id"])
            if row["policy_decision_id"]
            else None,
            idempotency_key=row["idempotency_key"],
            workflow_execution_reference=row["workflow_execution_reference"],
            external_reference=row["external_reference"],
            attempt_number=row["attempt_number"],
            status=ActionStatus(row["status"]),
            started_at=str_to_dt(row["started_at"]),
            completed_at=str_to_dt(row["completed_at"]),
            failure_reason=row["failure_reason"],
        )
