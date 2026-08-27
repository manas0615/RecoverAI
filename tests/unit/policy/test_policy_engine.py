from datetime import datetime, timezone
import uuid

import pytest

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.assessment import AnalysisType, CauseAssessment, RiskAssessment
from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryCaseStatus,
    RevenueSource,
)
from recoverai.domain.evidence import Probability
from recoverai.domain.identifiers import (
    MerchantId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)
from recoverai.domain.policy import PolicyDecisionValue
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.policy import PolicyDecisionRepository
from recoverai.policy.engine import PolicyContext, PolicyEngine


@pytest.fixture
def policy_engine() -> PolicyEngine:
    return PolicyEngine(generate_decision_id=lambda: f"pd_{uuid.uuid4().hex[:8]}")


@pytest.fixture
def default_context() -> PolicyContext:
    return PolicyContext(
        policy_version="1.0",
        current_time=datetime.now(timezone.utc),
        max_attempts_per_case=3,
        high_value_threshold=RevenueAmount(Money(100000, CurrencyCode.INR)),
    )


@pytest.fixture
def base_case() -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("merch_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=datetime.now(timezone.utc),
        source_event_ids={RevenueEventId("evt_1")},
        workflow_state=CaseWorkflowState.PLANNING,
    )


def build_plan(case_id: RecoveryCaseId, action_type: ActionType) -> InterventionPlan:
    cand = InterventionCandidate(
        candidate_id="cand_1",
        case_id=case_id,
        action_type=action_type,
        expected_recovery_probability=Probability(0.8, "recovery"),
        expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.INR)),
        eligibility_status=CandidateStatus.PROPOSED,
    )
    return InterventionPlan(
        plan_id="plan_1",
        case_id=case_id,
        candidates=[cand],
        selected_action_type=action_type,
        selection_reason="Test plan",
        selection_model_version="1.0",
        created_at=datetime.now(timezone.utc),
    )


def test_terminal_case_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: CASE_TERMINAL
    P05 Terminal cases cannot be evaluated for new actions.
    """
    # Close the case directly
    from recoverai.domain.case import RecoveryOutcomeValue

    base_case.close(
        RecoveryOutcomeValue.RECOVERED,
        default_context.current_time,
        RevenueAmount(Money(5000, CurrencyCode.INR)),
    )

    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    decision = policy_engine.evaluate(default_context, base_case, plan, [])

    assert decision.decision == PolicyDecisionValue.DENY
    assert "CASE_TERMINAL" in decision.reason_codes


def test_unknown_external_state_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: UNCERTAIN_EXTERNAL_STATE
    No blind duplicate financial mutation if the external state is unknown.
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    # Previous action of the SAME TYPE is EXECUTION_UNKNOWN
    unknown_action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=base_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=default_context.current_time,
        status=ActionStatus.EXECUTION_UNKNOWN,
    )

    decision = policy_engine.evaluate(
        default_context, base_case, plan, [unknown_action]
    )
    assert decision.decision == PolicyDecisionValue.DENY
    assert "UNCERTAIN_EXTERNAL_STATE" in decision.reason_codes


def test_duplicate_active_action_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: DUPLICATE_ACTIVE_RECOVERY_ACTION
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    # Active action of same type
    active_action = RecoveryAction(
        action_id=RecoveryActionId("act_2"),
        case_id=base_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=default_context.current_time,
        status=ActionStatus.EXECUTING,
    )

    decision = policy_engine.evaluate(default_context, base_case, plan, [active_action])
    assert decision.decision == PolicyDecisionValue.DENY
    assert "DUPLICATE_ACTIVE_RECOVERY_ACTION" in decision.reason_codes


def test_systemic_degradation_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: SYSTEMIC_DEGRADATION
    AI recommends a link, but systemic degradation is active.
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    cause = CauseAssessment(
        cause_assessment_id="cause_1",
        case_id=base_case.case_id,
        category="SYSTEMIC_DEGRADATION",
        confidence=Probability(0.9, "confidence"),
        analysis_type=AnalysisType.RULE_BASED,
        model_version="1.0",
        created_at=default_context.current_time,
    )

    decision = policy_engine.evaluate(default_context, base_case, plan, [], cause=cause)
    assert decision.decision == PolicyDecisionValue.SUPPRESS
    assert "SYSTEMIC_DEGRADATION" in decision.reason_codes


def test_attempt_limit_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: ATTEMPT_LIMIT_REACHED
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    # 3 prior actions
    history = [
        RecoveryAction(
            action_id=RecoveryActionId(f"act_{i}"),
            case_id=base_case.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            requested_at=default_context.current_time,
            status=ActionStatus.VERIFIED_FAILURE,
        )
        for i in range(3)
    ]

    decision = policy_engine.evaluate(default_context, base_case, plan, history)
    assert decision.decision == PolicyDecisionValue.SUPPRESS
    assert "ATTEMPT_LIMIT_REACHED" in decision.reason_codes


def test_high_value_escalation(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: HIGH_VALUE_ACTION
    """
    # Exceed threshold
    base_case.amount_at_risk = RevenueAmount(Money(100001, CurrencyCode.INR))
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    decision = policy_engine.evaluate(default_context, base_case, plan, [])
    assert decision.decision == PolicyDecisionValue.ESCALATE
    assert "HIGH_VALUE_ACTION" in decision.reason_codes


def test_currency_mismatch_fails_closed(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test: CURRENCY_MISMATCH_IN_POLICY
    """
    base_case.amount_at_risk = RevenueAmount(Money(5000, CurrencyCode.USD))
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    decision = policy_engine.evaluate(default_context, base_case, plan, [])
    assert decision.decision == PolicyDecisionValue.ESCALATE
    assert "CURRENCY_MISMATCH_IN_POLICY" in decision.reason_codes


def test_precedence_conflict_terminal_over_high_value(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    Test Precedence: Terminal case (DENY) overrides High Value (ESCALATE).
    """
    base_case.amount_at_risk = RevenueAmount(Money(100001, CurrencyCode.INR))
    from recoverai.domain.case import RecoveryOutcomeValue

    base_case.close(RecoveryOutcomeValue.SUPPRESSED, default_context.current_time)

    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)

    decision = policy_engine.evaluate(default_context, base_case, plan, [])
    assert decision.decision == PolicyDecisionValue.DENY
    assert "CASE_TERMINAL" in decision.reason_codes


def test_ai_bypass(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    """
    AI bypassed and tried to send a link during degradation. Policy should suppress.
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    cause = CauseAssessment(
        cause_assessment_id="cause_1",
        case_id=base_case.case_id,
        category="SYSTEMIC_DEGRADATION",
        confidence=Probability(0.99, "confidence"),
        analysis_type=AnalysisType.LLM,
        model_version="1.0",
        created_at=default_context.current_time,
    )
    decision = policy_engine.evaluate(default_context, base_case, plan, [], cause=cause)
    assert decision.decision == PolicyDecisionValue.SUPPRESS
    assert "SYSTEMIC_DEGRADATION" in decision.reason_codes


def test_policy_decision_persistence(
    policy_engine: PolicyEngine,
    default_context: PolicyContext,
    base_case: RecoveryCase,
    tm,
):
    """
    Test that PolicyDecision can be saved and retrieved.
    """
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    decision = policy_engine.evaluate(default_context, base_case, plan, [])

    # The case needs to exist in the database for foreign key constraint
    from recoverai.persistence.repositories.case import RecoveryCaseRepository

    with tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        base_case.merchant_id = MerchantId("m_1")  # use existing merchant
        # Actually it's easier just to insert case directly for test
        conn.execute(
            "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, workflow_state, version, opened_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                base_case.case_id.value,
                "m_1",
                base_case.revenue_source.value,
                base_case.amount_at_risk.amount_minor,
                base_case.amount_at_risk.currency.value,
                base_case.status.value,
                base_case.workflow_state.value,
                base_case.version,
                base_case.opened_at.isoformat(),
                base_case.opened_at.isoformat(),
            ),
        )
        repo = PolicyDecisionRepository(conn)
        repo.save(decision)

    with tm.transaction() as conn:
        repo = PolicyDecisionRepository(conn)
        saved = repo.get(decision.policy_decision_id)

    assert saved is not None
    assert saved.policy_decision_id == decision.policy_decision_id
    assert saved.decision == PolicyDecisionValue.APPROVE
    assert saved.policy_version == "1.0"
    assert "POLICY_APPROVED" in saved.reason_codes


def test_unknown_external_state_different_safe_action(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    plan = build_plan(base_case.case_id, ActionType.WAIT)
    unknown_action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=base_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=default_context.current_time,
        status=ActionStatus.EXECUTION_UNKNOWN,
    )
    decision = policy_engine.evaluate(
        default_context, base_case, plan, [unknown_action]
    )
    assert decision.decision == PolicyDecisionValue.APPROVE


def test_duplicate_active_action_different_type(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    plan = build_plan(base_case.case_id, ActionType.SEND_PAYMENT_LINK_NOTIFICATION)
    active_action = RecoveryAction(
        action_id=RecoveryActionId("act_2"),
        case_id=base_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=default_context.current_time,
        status=ActionStatus.VERIFICATION_PENDING,
    )
    decision = policy_engine.evaluate(default_context, base_case, plan, [active_action])
    assert decision.decision == PolicyDecisionValue.APPROVE


def test_systemic_degradation_over_attempt_limit(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    cause = CauseAssessment(
        cause_assessment_id="cause_1",
        case_id=base_case.case_id,
        category="SYSTEMIC_DEGRADATION",
        confidence=Probability(0.9, "confidence"),
        analysis_type=AnalysisType.RULE_BASED,
        model_version="1.0",
        created_at=default_context.current_time,
    )
    history = [
        RecoveryAction(
            action_id=RecoveryActionId(f"act_{i}"),
            case_id=base_case.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            requested_at=default_context.current_time,
            status=ActionStatus.VERIFIED_FAILURE,
        )
        for i in range(3)
    ]
    decision = policy_engine.evaluate(
        default_context, base_case, plan, history, cause=cause
    )
    assert decision.decision == PolicyDecisionValue.SUPPRESS
    assert decision.reason_codes == ["SYSTEMIC_DEGRADATION"]


def test_merchant_config_cannot_override_hard_safety(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    from dataclasses import replace

    high_limit_context = replace(default_context, max_attempts_per_case=100)
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    unknown_action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=base_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=default_context.current_time,
        status=ActionStatus.EXECUTION_UNKNOWN,
    )
    decision = policy_engine.evaluate(
        high_limit_context, base_case, plan, [unknown_action]
    )
    assert decision.decision == PolicyDecisionValue.DENY
    assert "UNCERTAIN_EXTERNAL_STATE" in decision.reason_codes


def test_caller_bypass_not_possible(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    from recoverai.domain.case import RecoveryOutcomeValue

    base_case.close(
        RecoveryOutcomeValue.RECOVERED,
        default_context.current_time,
        RevenueAmount(Money(5000, CurrencyCode.INR)),
    )
    plan = build_plan(base_case.case_id, ActionType.CREATE_PAYMENT_LINK)
    decision = policy_engine.evaluate(default_context, base_case, plan, [])
    assert decision.decision == PolicyDecisionValue.DENY


def test_policy_version_snapshot(
    policy_engine: PolicyEngine, default_context: PolicyContext, base_case: RecoveryCase
):
    plan = build_plan(base_case.case_id, ActionType.WAIT)
    decision1 = policy_engine.evaluate(default_context, base_case, plan, [])
    assert decision1.policy_version == "1.0"
    from dataclasses import replace

    new_context = replace(default_context, policy_version="2.0")
    decision2 = policy_engine.evaluate(new_context, base_case, plan, [])
    assert decision2.policy_version == "2.0"
