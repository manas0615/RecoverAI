import pytest
from datetime import UTC, datetime, timedelta
from fastapi.testclient import TestClient

from recoverai.api.main import app, container
from recoverai.config import settings
from recoverai.domain.case import CaseWorkflowState, RecoveryCaseStatus, RecoveryOutcomeValue
from recoverai.domain.event import RevenueEvent, RevenueEventType, EventSource, EventSourceType
from recoverai.domain.money import Money, CurrencyCode
from recoverai.domain.action import ActionStatus
from recoverai.domain.identifiers import MerchantId, RevenueEventId

def test_closed_loop_recovery_trigger():
    settings.enable_closed_loop_recovery = True
    
    with container.tm.transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_1', 'Test Merchant', 'INR', 'ACTIVE', '2023-01-01', '2023-01-01')")
    
    # 1. Simulate initial failure event
    event = RevenueEvent(
        event_id=RevenueEventId("evt_closed_loop_1"),
        merchant_id=MerchantId("merch_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "pay_1"),
        amount=Money(10000, CurrencyCode.INR),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC)
    )
    # mock action service execution to avoid Razorpay calls
    original_execute = container.action_service.execute_action
    def mock_execute(action):
        from recoverai.domain.action import ActionStatus
        action.status = ActionStatus.VERIFICATION_PENDING
        action.external_reference = "plink_mocked"
        with container.tm.transaction() as conn:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            RecoveryActionRepository(conn).save(action)
    container.action_service.execute_action = mock_execute
    
    # mock LLM gateway to avoid API calls and timeouts
    class MockGateway:
        def synthesize_cause(self, case, events, context):
            from recoverai.domain.assessment import CauseAssessment, CauseCategory, AnalysisType
            from recoverai.domain.evidence import Probability
            from datetime import datetime, UTC
            import uuid
            return CauseAssessment(
                cause_assessment_id=f"cause_{uuid.uuid4().hex[:12]}",
                case_id=case.case_id,
                category=CauseCategory.CUSTOMER_SPECIFIC, 
                confidence=Probability(0.9, "mock"), 
                analysis_type=AnalysisType.LLM,
                model_version="mock",
                created_at=datetime.now(UTC),
                evidence_references=[]
            )
            
        def generate_intervention_candidates(self, case, events, context, cause):
            from recoverai.domain.plan import InterventionCandidate, CandidateStatus
            from recoverai.domain.action import ActionType
            from recoverai.domain.evidence import Probability
            from recoverai.domain.money import RevenueAmount, Money, CurrencyCode
            return ("MockModel", [InterventionCandidate(
                candidate_id="ai_cand_1",
                case_id=case.case_id,
                action_type=ActionType.CREATE_PAYMENT_LINK,
                expected_recovery_probability=Probability(0.9, "mock"),
                expected_recovery_value=RevenueAmount(Money(100, CurrencyCode.INR)),
                eligibility_status=CandidateStatus.PROPOSED,
                reason="mock",
                evidence_references=[]
            )])
            
    container.intelligence.llm_gateway = MockGateway()

    
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository
        RevenueEventRepository(conn).save(event)
    
    case = container.case_manager.create_or_update_from_event(event)
    container.global_conn.commit()
    
    # 2. Simulate analysis (manual call for tests instead of background task)
    from recoverai.api.main import analyze_case
    import asyncio
    asyncio.run(analyze_case(str(case.case_id.value)))
    
    # The action should now be created and executing
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        
        actions = action_repo.get_by_case(case.case_id)
        assert len(actions) == 1
        
        # Advance state simulating Razorpay mock
        action = actions[0]
        # We simulate that this action created a payment link (e.g. plink_mocked)
        action.external_reference = "plink_mocked"
        action.status = ActionStatus.VERIFICATION_PENDING
        action_repo.save(action)
        
        c = case_repo.get(case.case_id)
        c.workflow_state = CaseWorkflowState.VERIFYING
        case_repo.save(c)
        
    # 3. Simulate recovery payment failure webhook
    failure_event = RevenueEvent(
        event_id=RevenueEventId("evt_closed_loop_2"),
        merchant_id=MerchantId("merch_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "pay_2"),
        amount=Money(10000, CurrencyCode.INR),
        metadata={"payload": {"payment": {"entity": {"description": "#mocked"}}}}, # matching plink_mocked
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC)
    )
    with container.tm.transaction() as conn:
        RevenueEventRepository(conn).save(failure_event)
        
    updated_case = container.case_manager.create_or_update_from_event(failure_event)
    container.global_conn.commit()
    
    assert updated_case is not None
    assert updated_case.case_id == case.case_id
    assert updated_case.workflow_state == CaseWorkflowState.PLANNING
    # Ensure event was added
    assert failure_event.event_id in updated_case.source_event_ids
    
    # 4. Trigger analysis again
    asyncio.run(analyze_case(str(case.case_id.value)))
    
    with container.tm.transaction() as conn:
        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        actions_after = action_repo.get_by_case(case.case_id)
        assert len(actions_after) == 2
        
        # We manually test limit of 3. Let's force it to 3 attempts.
        from recoverai.domain.action import RecoveryAction, RecoveryActionId, ActionType
        import uuid
        action3 = RecoveryAction(
            action_id=RecoveryActionId(f"act_{uuid.uuid4().hex[:12]}"),
            case_id=case.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            requested_at=datetime.now(UTC),
            status=ActionStatus.VERIFIED_FAILURE,
            attempt_number=3
        )
        action_repo.save(action3)
    
    # 5. Now 3 attempts reached (1 + 2 mocked). If we trigger analysis, it should SUPPRESS and CLOSE case.
    asyncio.run(analyze_case(str(case.case_id.value)))
    
    with container.tm.transaction() as conn:
        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        final_case = case_repo.get(case.case_id)
        assert final_case.status == RecoveryCaseStatus.CLOSED
        assert final_case.outcome_type == RecoveryOutcomeValue.SUPPRESSED
        
        # Number of actions shouldn't increase
        actions_final = action_repo.get_by_case(case.case_id)
        assert len(actions_final) == 3
