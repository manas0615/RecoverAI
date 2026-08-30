import os
import sys
import asyncio
from datetime import UTC, datetime
from uuid import uuid4

# Setup sys path so we can import recoverai
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recoverai.config import settings
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.event import RevenueEventRepository
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.policy.engine import PolicyEngine, PolicyContext
from recoverai.application.action_service import RecoveryActionService
from recoverai.integrations.razorpay.adapter import RazorpayAdapter, RazorpayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.llm_gateway.providers import GeminiAdapter
from recoverai.domain.action import RecoveryAction, ActionType, ActionStatus, RecoveryActionId
from recoverai.domain.case import RecoveryCaseId, CaseWorkflowState

def run_test():
    # 1. Setup components
    tm = TransactionManager(settings.database_url)
    rzp_config = RazorpayConfig(
        key_id=settings.razorpay_key_id,
        key_secret=settings.razorpay_key_secret,
        mode=settings.razorpay_mode
    )
    adapter = RazorpayAdapter(rzp_config)
    policy_engine = PolicyEngine(generate_decision_id=lambda: f"pol_{uuid4().hex[:12]}")
    action_service = RecoveryActionService(tm, policy_engine, adapter)
    
    from recoverai.llm_gateway.config import GatewayConfig
    gateway_config = GatewayConfig.from_env()
    gateway = ConcreteLLMGateway(gateway_config)
    analyzer = RevenueIntelligenceAnalyzer(gateway)
    
    # 2. Get Case LIVE
    with tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        case = case_repo.get(RecoveryCaseId("case_LIVE"))
        if not case:
            print("Case LIVE not found.")
            return
            
        event_repo = RevenueEventRepository(conn)
        events = [e for e in (event_repo.get(eid) for eid in case.source_event_ids) if e]
        
        print(f"Executing Razorpay on {case.case_id.value} for {case.amount_at_risk.amount_minor} {case.amount_at_risk.currency.value}")
        
    # 3. Analyze Case (AI Grounding)
    risk, cause, plan = analyzer.analyze(case, events)
    print("Intelligence Plan:")
    print(plan)
    
    # 4. Propose action
    action_id = f"act_{uuid4().hex[:12]}"
    action = RecoveryAction(
        action_id=RecoveryActionId(action_id),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.PROPOSED,
        requested_at=datetime.now(UTC),
        idempotency_key=action_id
    )
    action._real_plan = plan
    
    # 5. Save action initially
    with tm.transaction() as conn:
        action_repo = RecoveryActionRepository(conn)
        action_repo.save(action)
    
    # 6. Execute!
    try:
        print("Calling ActionService.execute_action...")
        executed_action = action_service.execute_action(action)
        print(f"Action Status: {executed_action.status}")
        print(f"External Reference: {executed_action.external_reference}")
        print(f"Failure Reason: {executed_action.failure_reason}")
    except Exception as e:
        print(f"Exception during execution: {e}")

if __name__ == "__main__":
    run_test()
