import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from recoverai.api.main import container
from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.audit import (
    AuditActor,
    AuditActorType,
    AuditEvent,
    AuditEventType,
)
from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryOutcomeValue,
    RevenueSource,
)
from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.identifiers import (
    CustomerId,
    MerchantId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
    VerificationRecordId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.verification import (
    VerificationRecord,
    VerificationSource,
    VerifiedState,
)
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository
from recoverai.persistence.repositories.verification import VerificationRecordRepository


def create_base_case(
    conn, scenario_name: str, amount_minor: int, offset_minutes: int = 0
):
    merchant_id = MerchantId("merch_demo")
    customer_id = CustomerId("cust_demo")

    now = datetime.now(UTC) - timedelta(minutes=offset_minutes)

    event_id = RevenueEventId(f"evt_{scenario_name}")
    payment_id = f"pay_{scenario_name}"

    event = RevenueEvent(
        event_id=event_id,
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(
            source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id=payment_id
        ),
        merchant_id=merchant_id,
        customer_id=customer_id,
        amount=Money(amount_minor, CurrencyCode.INR),
        occurred_at=now,
        received_at=now,
        schema_version="1.0",
    )
    RevenueEventRepository(conn).save(event)

    case = RecoveryCase(
        case_id=RecoveryCaseId(f"case_{scenario_name}"),
        merchant_id=merchant_id,
        customer_id=customer_id,
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(amount_minor, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={event_id},
    )
    RecoveryCaseRepository(conn).save(case)
    return case, now


def add_audit(conn, event_type, case_id, action_id=None, metadata=None, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(UTC)
    meta = dict(metadata or {})
    new_state = meta.pop("new_state", None)
    previous_state = meta.pop("previous_state", None)
    AuditRepository(conn).append(
        AuditEvent(
            event_type=event_type,
            actor=AuditActor(type=AuditActorType.SYSTEM, id="seed"),
            case_id=case_id,
            action_id=action_id,
            new_state=new_state,
            previous_state=previous_state,
            metadata=meta,
            timestamp=timestamp,
        )
    )


def seed_data():
    merchant_id = MerchantId("merch_demo")
    customer_id = CustomerId("cust_demo")

    with container.tm.transaction() as conn:
        conn.execute("DELETE FROM verification_records")
        conn.execute("DELETE FROM recovery_actions")
        conn.execute("DELETE FROM policy_decisions")
        conn.execute("DELETE FROM intervention_plan_candidates")
        conn.execute("DELETE FROM intervention_plans")
        conn.execute("DELETE FROM intervention_candidates")
        conn.execute("DELETE FROM cause_assessments")
        conn.execute("DELETE FROM risk_assessments")
        conn.execute("DELETE FROM case_source_events")
        conn.execute("DELETE FROM recovery_cases")
        conn.execute("DELETE FROM revenue_events")
        conn.execute("DELETE FROM audit_events")

        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                merchant_id.value,
                "Demo Merchant",
                "INR",
                "ACTIVE",
                datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (customer_id, merchant_id, display_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (
                customer_id.value,
                merchant_id.value,
                "Demo Customer",
                datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat(),
            ),
        )

        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        vr_repo = VerificationRecordRepository(conn)

        # SCENARIO A — SUCCESS
        case_a, t_a = create_base_case(conn, "SUCCESS", 50000, 120)
        action_a = RecoveryAction(
            action_id=RecoveryActionId("act_SUCCESS"),
            case_id=case_a.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_a,
            external_reference="plink_success",
        )
        action_a.authorize(PolicyDecisionId("dec_SUCCESS"), t_a)

        conn.execute(
            """INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dec_SUCCESS",
                case_a.case_id.value,
                action_a.action_id.value,
                "APPROVE",
                "1.0",
                "[]",
                "[]",
                t_a.isoformat(),
            ),
        )

        action_a.begin_execution(t_a + timedelta(minutes=1))
        action_a.record_verification(
            ActionStatus.VERIFICATION_PENDING, t_a + timedelta(minutes=2)
        )
        action_a.record_verification(
            ActionStatus.VERIFIED_SUCCESS, t_a + timedelta(minutes=5)
        )
        action_repo.save(action_a)

        case_a.advance_workflow(CaseWorkflowState.VERIFYING, t_a + timedelta(minutes=2))
        case_a.close(
            RecoveryOutcomeValue.RECOVERED,
            t_a + timedelta(minutes=5),
            RevenueAmount(Money(50000, CurrencyCode.INR)),
        )
        case_repo.save(case_a)

        vr_repo.save(
            VerificationRecord(
                verification_id=VerificationRecordId("vr_SUCCESS"),
                action_id=action_a.action_id,
                case_id=case_a.case_id,
                verification_source=VerificationSource.SIMULATOR,
                verified_state=VerifiedState.SUCCESS,
                checked_at=t_a + timedelta(minutes=5),
            )
        )
        add_audit(conn, AuditEventType.CASE_CREATED, case_a.case_id, timestamp=t_a)
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_a.case_id,
            action_a.action_id,
            {"decision": "APPROVE"},
            t_a + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.ACTION_EXECUTING,
            case_a.case_id,
            action_a.action_id,
            {"provider": "razorpay"},
            t_a + timedelta(minutes=1, seconds=30),
        )
        add_audit(
            conn,
            AuditEventType.RAZORPAY_REQUEST_COMPLETED,
            case_a.case_id,
            action_a.action_id,
            {"provider_reference": "plink_success"},
            t_a + timedelta(minutes=2),
        )
        add_audit(
            conn,
            AuditEventType.VERIFICATION_COMPLETED,
            case_a.case_id,
            action_a.action_id,
            {"new_state": "VERIFIED_SUCCESS"},
            t_a + timedelta(minutes=5),
        )
        add_audit(
            conn,
            AuditEventType.RECOVERY_CONFIRMED,
            case_a.case_id,
            action_a.action_id,
            timestamp=t_a + timedelta(minutes=5),
        )

        # SCENARIO B — PROVIDER FAILURE
        case_b, t_b = create_base_case(conn, "FAILURE", 120000, 100)
        action_b = RecoveryAction(
            action_id=RecoveryActionId("act_FAILURE"),
            case_id=case_b.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_b,
        )
        action_b.authorize(PolicyDecisionId("dec_FAILURE"), t_b)
        conn.execute(
            """INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dec_FAILURE",
                case_b.case_id.value,
                action_b.action_id.value,
                "APPROVE",
                "1.0",
                "[]",
                "[]",
                t_b.isoformat(),
            ),
        )
        action_b.begin_execution(t_b + timedelta(minutes=1))
        action_b.record_verification(
            ActionStatus.VERIFIED_FAILURE, t_b + timedelta(minutes=2)
        )
        action_b.failure_reason = "Validation Error"
        action_repo.save(action_b)

        case_b.advance_workflow(
            CaseWorkflowState.VERIFYING, t_b + timedelta(minutes=1, seconds=30)
        )
        case_b.close(RecoveryOutcomeValue.NOT_RECOVERED, t_b + timedelta(minutes=2))
        case_repo.save(case_b)

        add_audit(conn, AuditEventType.CASE_CREATED, case_b.case_id, timestamp=t_b)
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_b.case_id,
            action_b.action_id,
            {"decision": "APPROVE"},
            t_b + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.VERIFICATION_COMPLETED,
            case_b.case_id,
            action_b.action_id,
            {"new_state": "VERIFIED_FAILURE", "error": "Validation Error"},
            t_b + timedelta(minutes=2),
        )

        # SCENARIO C — EXECUTION_UNKNOWN
        case_c, t_c = create_base_case(conn, "UNKNOWN", 85000, 80)
        action_c = RecoveryAction(
            action_id=RecoveryActionId("act_UNKNOWN"),
            case_id=case_c.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_c,
        )
        action_c.authorize(PolicyDecisionId("dec_UNKNOWN"), t_c)
        conn.execute(
            """INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dec_UNKNOWN",
                case_c.case_id.value,
                action_c.action_id.value,
                "APPROVE",
                "1.0",
                "[]",
                "[]",
                t_c.isoformat(),
            ),
        )
        action_c.begin_execution(t_c + timedelta(minutes=1))
        action_c.record_verification(
            ActionStatus.EXECUTION_UNKNOWN, t_c + timedelta(minutes=2)
        )
        action_c.failure_reason = "Timeout"

        action_repo.save(action_c)

        case_c.advance_workflow(CaseWorkflowState.UNKNOWN, t_c + timedelta(minutes=2))
        case_repo.save(case_c)

        add_audit(conn, AuditEventType.CASE_CREATED, case_c.case_id, timestamp=t_c)
        add_audit(
            conn,
            AuditEventType.RECOVERY_STATE_CHANGED,
            case_c.case_id,
            action_c.action_id,
            {"new_state": "UNKNOWN"},
            t_c + timedelta(minutes=2),
        )
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_c.case_id,
            action_c.action_id,
            {"decision": "APPROVE"},
            t_c + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.ACTION_EXECUTION_UNKNOWN,
            case_c.case_id,
            action_c.action_id,
            {"error": "Timeout"},
            t_c + timedelta(minutes=2),
        )

        # SCENARIO D — POLICY DENIAL
        case_d, t_d = create_base_case(conn, "DENIAL", 45000, 60)
        action_d = RecoveryAction(
            action_id=RecoveryActionId("act_DENIAL"),
            case_id=case_d.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_d,
        )
        # Denied by policy, so we skip authorize/execution and just record cancellation
        action_d.record_verification(ActionStatus.CANCELLED, t_d + timedelta(minutes=1))

        action_repo.save(action_d)

        case_d.close(RecoveryOutcomeValue.SUPPRESSED, t_d + timedelta(minutes=1))
        case_repo.save(case_d)

        conn.execute(
            """INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dec_DENIAL",
                case_d.case_id.value,
                action_d.action_id.value,
                "DENY",
                "1.0",
                "[]",
                "[]",
                t_d.isoformat(),
            ),
        )

        add_audit(conn, AuditEventType.CASE_CREATED, case_d.case_id, timestamp=t_d)
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_d.case_id,
            action_d.action_id,
            {"decision": "DENY", "reason": "DUPLICATE_ACTIVE_RECOVERY_ACTION"},
            t_d + timedelta(minutes=1),
        )

        # SCENARIO E — HUMAN ESCALATION

        case_e, t_e = create_base_case(conn, "ESCALATION", 5000000, 40)
        action_e = RecoveryAction(
            action_id=RecoveryActionId("act_ESCALATION"),
            case_id=case_e.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_e,
        )

        # Policy escalates it
        conn.execute(
            """INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dec_ESCALATE",
                case_e.case_id.value,
                action_e.action_id.value,
                "ESCALATE",
                "1.0",
                "[]",
                "[]",
                t_e.isoformat(),
            ),
        )
        # It stays proposed/escalated, no execution yet
        action_repo.save(action_e)

        case_e.advance_workflow(
            CaseWorkflowState.WAITING_APPROVAL, t_e + timedelta(minutes=1)
        )
        case_repo.save(case_e)

        add_audit(conn, AuditEventType.CASE_CREATED, case_e.case_id, timestamp=t_e)
        add_audit(
            conn,
            AuditEventType.RECOVERY_STATE_CHANGED,
            case_e.case_id,
            action_e.action_id,
            {"new_state": "WAITING_APPROVAL"},
            t_e + timedelta(minutes=1, seconds=30),
        )
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_e.case_id,
            action_e.action_id,
            {"decision": "ESCALATE", "reason": "HIGH_VALUE_ACTION"},
            t_e + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.CASE_ESCALATED,
            case_e.case_id,
            action_e.action_id,
            timestamp=t_e + timedelta(minutes=1),
        )

        # SCENARIO F — DUPLICATE/IDEMPOTENCY
        case_f, t_f = create_base_case(conn, "DUPLICATE", 25000, 30)

        # Simulate receiving a duplicate webhook. It fails to insert (idempotency),
        # so the system only logs an audit event indicating a duplicate was received.
        add_audit(conn, AuditEventType.CASE_CREATED, case_f.case_id, timestamp=t_f)
        add_audit(
            conn,
            AuditEventType.WEBHOOK_DUPLICATE,
            case_f.case_id,
            None,
            {"duplicate_of": "evt_DUPLICATE"},
            t_f + timedelta(minutes=5),
        )

        # SCENARIO G — LIVE DETECTED/ANALYZE
        case_g, t_g = create_base_case(conn, "LIVE", 100000, 10)
        # We explicitly DO NOT add an LLM recommendation or proposed action.
        # The UI will let the user click "Analyze Case" to trigger one.
        add_audit(conn, AuditEventType.CASE_CREATED, case_g.case_id, timestamp=t_g)
        add_audit(
            conn,
            AuditEventType.WEBHOOK_RECEIVED,
            case_g.case_id,
            None,
            {"event_type": "payment.failed"},
            t_g + timedelta(seconds=2),
        )

        print("Seeded Demo Data successfully.")


if __name__ == "__main__":
    seed_data()
