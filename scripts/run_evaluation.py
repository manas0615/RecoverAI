import argparse
from recoverai.evaluation.benchmark import run_benchmark
from recoverai.evaluation.simulator import SyntheticScenarioGenerator
from recoverai.evaluation.evaluator import Evaluator
from recoverai.evaluation.strategies import L0NoIntervention, L1NaiveRule, L2DeterministicRules, L3CurrentRecoverAI, L3ControlledAIRecoverAI, EvaluationStrategy, StrategyDecision, build_case_and_events
from recoverai.evaluation.simulator import ObservableCaseEvidence
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.policy.engine import PolicyEngine, PolicyContext
from recoverai.domain.policy import PolicyDecisionValue
from recoverai.domain.money import RevenueAmount, CurrencyCode, Money
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from datetime import datetime, UTC

class HybridLiveGeminiStrategy(EvaluationStrategy):
    def __init__(self, limit: int):
        self.limit = limit
        self.live_calls = 0
        
        # Real Gemini Gateway
        config = GatewayConfig.from_env()
        self.live_gateway = ConcreteLLMGateway(config)
        
        self.policy_engine = PolicyEngine(generate_decision_id=lambda: "dec_hybrid")
        self.policy_context = PolicyContext(
            policy_version="1.0",
            current_time=datetime.now(UTC),
            max_attempts_per_case=3,
            high_value_threshold=RevenueAmount(Money(40000_00, CurrencyCode.INR))
        )

    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        case, events, action_history = build_case_and_events(evidence)
        
        if self.live_calls < self.limit:
            # Use Live Gemini
            analyzer = RevenueIntelligenceAnalyzer(llm_gateway=self.live_gateway)
            self.live_calls += 1
            used_live = True
        else:
            # Use Fallback
            analyzer = RevenueIntelligenceAnalyzer(llm_gateway=None)
            used_live = False
            
        try:
            risk, cause, plan = analyzer.analyze(case, events)
            decision = self.policy_engine.evaluate(self.policy_context, case, plan, action_history, cause)
            
            if decision.decision == PolicyDecisionValue.APPROVE:
                action = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
            else:
                action = decision.decision.value
                
            probability = 0.0
            if plan.candidates:
                probability = plan.candidates[0].expected_recovery_probability.value

            proposed = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
            
            source = "REAL_GEMINI_AI" if used_live else "DETERMINISTIC_FALLBACK"
            if used_live and cause and cause.analysis_type.name != "LLM":
                source = "GEMINI_FAILED_FALLBACK"

            return StrategyDecision(
                action_taken=action,
                probability=probability,
                probability_source=source,
                recommendation_source=source,
                proposed_action=proposed
            )
        except Exception as e:
            # If Gemini outright crashes, fallback gracefully to deterministic
            print(f"Warning: Live AI failed, using fallback: {e}")
            fallback_analyzer = RevenueIntelligenceAnalyzer(llm_gateway=None)
            risk, cause, plan = fallback_analyzer.analyze(case, events)
            decision = self.policy_engine.evaluate(self.policy_context, case, plan, action_history, cause)
            if decision.decision == PolicyDecisionValue.APPROVE:
                action = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
            else:
                action = decision.decision.value
            return StrategyDecision(
                action_taken=action,
                probability=0.0,
                probability_source="GEMINI_FAILED_FALLBACK",
                recommendation_source="GEMINI_FAILED_FALLBACK",
                proposed_action=plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
            )

def run_hybrid_evaluation(seed: int, count: int, llm_limit: int):
    generator = SyntheticScenarioGenerator(seed=seed)
    scenarios = generator.generate(count)
    
    evaluator = Evaluator()
    strategy = HybridLiveGeminiStrategy(limit=llm_limit)
    
    metrics = evaluator.evaluate(strategy, scenarios)
    
    print("\n--- Hybrid AI Evaluation Validation ---")
    print(f"Total Scenarios: {metrics.eligible_cases}")
    print(f"Live Gemini Invocations Attempted: {strategy.live_calls}")
    print(f"Remaining Fallback Cases: {metrics.eligible_cases - strategy.live_calls}")
    print(f"Gross Recovery Simulated: {metrics.gross_recovered_value}")
    print(f"Policy Violations: {metrics.policy_violations}")
    print(f"Oracle Agreement: {metrics.decision_quality_rate * 100:.1f}%")
    print(f"Safety Pass: {metrics.passed_safety_invariants}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RecoverAI")
    parser.add_argument("--hybrid-ai", action="store_true", help="Run hybrid AI evaluation")
    parser.add_argument("--llm-limit", type=int, default=10, help="Number of real Gemini calls to make")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for scenarios")
    parser.add_argument("--count", type=int, default=1500, help="Number of scenarios")
    args = parser.parse_args()

    if args.hybrid_ai:
        run_hybrid_evaluation(args.seed, args.count, args.llm_limit)
    else:
        results = run_benchmark(args.seed, args.count)
        print(f"--- Benchmark Validation Run ---")
        print(f"Seed: {results['metadata']['seed']}, Scenarios: {results['metadata']['scenario_count']}")
        
        for level in ["L0", "L1", "L2", "L3"]:
            m = results[level]
            print(f"\n[{level}] Gross Recovery: {m.gross_recovered_value} | Interventions: {m.interventions} | False Recovery: {m.false_recovery_claims} | Policy Viol: {m.policy_violations} | Oracle Agreement: {m.decision_quality_rate * 100:.1f}%")
