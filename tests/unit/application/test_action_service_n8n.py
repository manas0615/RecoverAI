from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from recoverai.application.action_service import RecoveryActionService
from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.audit import AuditEventType
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.identifiers import (
    MerchantId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository


def test_n8n_trigger_failure_writes_failed_event(tm):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("Mock HTTP Error")

        with tm.transaction() as conn:
            conn.execute(
                "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, occurred_at, received_at, metadata, schema_version) VALUES ('evt_1', 'PAYMENT_FAILED', 'WEBHOOK', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', '{}', '1.0')"
            )
            case = RecoveryCase(
                case_id=RecoveryCaseId("case_n8n_1"),
                merchant_id=MerchantId("m_1"),
                revenue_source=RevenueSource.PAYMENT,
                amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
                opened_at=datetime.now(UTC),
                source_event_ids={RevenueEventId("evt_1")},
            )
            RecoveryCaseRepository(conn).save(case)

            action = RecoveryAction(
                action_id=RecoveryActionId("act_n8n_1"),
                case_id=case.case_id,
                action_type=ActionType.CREATE_PAYMENT_LINK,
                requested_at=datetime.now(UTC),
                status=ActionStatus.PROPOSED,
                attempt_number=1,
            )
            RecoveryActionRepository(conn).save(action)

        decision = PolicyDecision(
            policy_decision_id=PolicyDecisionId("pd_1"),
            case_id=case.case_id,
            action_id_or_proposal_id=action.action_id.value,
            decision=PolicyDecisionValue.ESCALATE,
            policy_version="1.0",
            evaluated_at=datetime.now(UTC),
        )
        from recoverai.domain.evidence import Probability
        from recoverai.domain.plan import (
            CandidateStatus,
            InterventionCandidate,
            InterventionPlan,
        )

        plan = InterventionPlan(
            plan_id="plan_1",
            case_id=case.case_id,
            candidates=[
                InterventionCandidate(
                    candidate_id="cand_1",
                    case_id=case.case_id,
                    action_type=ActionType.CREATE_PAYMENT_LINK,
                    expected_recovery_probability=Probability(0.9, "high"),
                    expected_recovery_value=RevenueAmount(
                        Money(5000, CurrencyCode.INR)
                    ),
                    eligibility_status=CandidateStatus.PROPOSED,
                )
            ],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="Test",
            selection_model_version="1.0",
            created_at=datetime.now(UTC),
        )
        action._real_plan = plan

        from recoverai.integrations.razorpay.adapter import RazorpayAdapter
        from recoverai.policy.engine import PolicyEngine

        mock_policy = MagicMock(spec=PolicyEngine)
        mock_policy.evaluate.return_value = decision
        mock_adapter = MagicMock(spec=RazorpayAdapter)
        service = RecoveryActionService(tm, mock_policy, mock_adapter)
        service.execute_action(action)

        with tm.transaction() as conn:
            audits = AuditRepository(conn).get_by_case(case.case_id.value)
            event_types = [a.event_type for a in audits]

            assert AuditEventType.CASE_ESCALATED in event_types
            assert AuditEventType.WORKFLOW_TRIGGER_FAILED in event_types
            assert AuditEventType.WORKFLOW_STARTED not in event_types
