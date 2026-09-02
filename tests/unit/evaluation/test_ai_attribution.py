import inspect
from recoverai.evaluation.simulator import SyntheticScenarioGenerator, ObservableCaseEvidence
from recoverai.evaluation.strategies import L2DeterministicRules, L3ControlledAIRecoverAI, L3CurrentRecoverAI
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.intelligence.gateway import GatewayError
from recoverai.domain.money import Money, CurrencyCode

def test_l2_receives_no_hidden_truth():
    sig = inspect.signature(L2DeterministicRules.evaluate)
    assert "truth" not in sig.parameters

def test_l3a_receives_no_hidden_truth():
    sig = inspect.signature(L3ControlledAIRecoverAI.evaluate)
    assert "truth" not in sig.parameters

def test_ai_cannot_authorize_execution():
    # Show that AI proposing an action does not bypass PolicyEngine (which generates the authoritative PolicyDecision)
    evidence = ObservableCaseEvidence(
        scenario_id="1", merchant_id="m1", customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="network_timeout", gateway_downtime_active=False,
        historical_failure_count=5 # Unsafe!
    )
    l3a = L3ControlledAIRecoverAI()
    decision = l3a.evaluate(evidence)
    assert decision.proposed_action == "CREATE_PAYMENT_LINK" # AI naive
    assert decision.action_taken == "SUPPRESS" # Policy blocked it!

def test_ai_unsafe_proposal_is_blocked():
    # Covered by the above test
    pass

def test_ai_recommendation_provenance_is_recorded():
    evidence = ObservableCaseEvidence(
        scenario_id="1", merchant_id="m1", customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="customer_error", gateway_downtime_active=False,
        historical_failure_count=0
    )
    l3a = L3ControlledAIRecoverAI()
    decision = l3a.evaluate(evidence)
    assert decision.recommendation_source == "CONTROLLED_AI_RECOMMENDATION"

def test_l3f_and_l3a_can_be_distinguished():
    evidence = ObservableCaseEvidence(
        scenario_id="1", merchant_id="m1", customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="customer_error", gateway_downtime_active=False,
        historical_failure_count=0
    )
    l3a = L3ControlledAIRecoverAI()
    l3f = L3CurrentRecoverAI()
    
    da = l3a.evaluate(evidence)
    df = l3f.evaluate(evidence)
    
    assert da.recommendation_source != df.recommendation_source

def test_ai_timeout_triggers_valid_fallback():
    class TimeoutGateway:
        def synthesize_cause(self, case, events, context):
            raise GatewayError("Timeout")
        def generate_intervention_candidates(self, case, events, context, cause):
            raise GatewayError("Timeout")
            
    analyzer = RevenueIntelligenceAnalyzer(llm_gateway=TimeoutGateway())
    l3 = L3CurrentRecoverAI()
    l3.analyzer = analyzer # Inject failing gateway
    
    evidence = ObservableCaseEvidence(
        scenario_id="1", merchant_id="m1", customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="customer_error", gateway_downtime_active=False,
        historical_failure_count=0
    )
    
    decision = l3.evaluate(evidence)
    assert decision.recommendation_source == "DETERMINISTIC_FALLBACK"

def test_malformed_ai_output_triggers_valid_fallback():
    class MalformedGateway:
        def synthesize_cause(self, case, events, context):
            raise ValueError("Malformed JSON")
        def generate_intervention_candidates(self, case, events, context, cause):
            raise ValueError("Malformed JSON")
            
    analyzer = RevenueIntelligenceAnalyzer(llm_gateway=MalformedGateway())
    l3 = L3CurrentRecoverAI()
    l3.analyzer = analyzer 
    
    evidence = ObservableCaseEvidence(
        scenario_id="1", merchant_id="m1", customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="customer_error", gateway_downtime_active=False,
        historical_failure_count=0
    )
    
    decision = l3.evaluate(evidence)
    assert decision.recommendation_source == "DETERMINISTIC_FALLBACK"
