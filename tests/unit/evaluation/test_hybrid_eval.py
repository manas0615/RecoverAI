import pytest
from recoverai.evaluation.simulator import SyntheticScenarioGenerator
from recoverai.evaluation.evaluator import Evaluator
from scripts.run_evaluation import HybridLiveGeminiStrategy
import builtins

def test_hybrid_evaluation_counts(monkeypatch):
    # We want to mock ConcreteLLMGateway to just return something or mock analyze
    
    class MockGateway:
        def synthesize_cause(self, case, events, context):
            from recoverai.domain.assessment import CauseAssessment, CauseCategory, AnalysisType
            from recoverai.domain.evidence import Probability
            return CauseAssessment(category=CauseCategory.CUSTOMER_ERROR, confidence=Probability(0.9, "mock"), analysis_type=AnalysisType.LLM)
            
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

    from recoverai.llm_gateway.engine import ConcreteLLMGateway
    monkeypatch.setattr("scripts.run_evaluation.ConcreteLLMGateway", lambda x: MockGateway())

    generator = SyntheticScenarioGenerator(seed=1)
    scenarios = generator.generate(15)
    
    evaluator = Evaluator()
    strategy = HybridLiveGeminiStrategy(limit=5)
    
    # We override the live_gateway with MockGateway
    strategy.live_gateway = MockGateway()
    
    metrics = evaluator.evaluate(strategy, scenarios)
    
    assert strategy.live_calls == 5
    assert metrics.eligible_cases == 15
    assert metrics.passed_safety_invariants

def test_hybrid_evaluation_gateway_failure(monkeypatch):
    class FailingGateway:
        def synthesize_cause(self, case, events, context):
            raise ValueError("API Error")
            
    monkeypatch.setattr("scripts.run_evaluation.ConcreteLLMGateway", lambda x: FailingGateway())
    
    generator = SyntheticScenarioGenerator(seed=2)
    scenarios = generator.generate(2)
    
    evaluator = Evaluator()
    strategy = HybridLiveGeminiStrategy(limit=2)
    strategy.live_gateway = FailingGateway()
    
    # Should not crash, should fallback
    metrics = evaluator.evaluate(strategy, scenarios)
    assert strategy.live_calls == 2
    assert metrics.eligible_cases == 2
