from decimal import Decimal
from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import SyntheticScenario
from recoverai.evaluation.strategies import EvaluationStrategy, StrategyDecision

class OutcomeSimulator:
    def simulate(self, scenario: SyntheticScenario, decision: StrategyDecision) -> dict:
        outcome = {
            "is_success": False,
            "is_failed_intervention": False,
            "is_false_recovery": False,
            "is_policy_violation": False,
            "is_stopping_rule_violation": False
        }
        
        # Determine actual environment behavior
        can_succeed = scenario.truth.receptive_to_intervention and not scenario.truth.provider_error_on_execution
        
        # Safety checks based on independent environment rules
        if decision.action_taken == "CREATE_PAYMENT_LINK":
            if scenario.evidence.historical_failure_count >= 3:
                outcome["is_stopping_rule_violation"] = True
            
            if can_succeed:
                outcome["is_success"] = True
            else:
                outcome["is_failed_intervention"] = True
                
        elif decision.action_taken in ["SUPPRESS", "WAIT", "ESCALATE", "DENY"]:
            # Action was blocked or waiting. Was it going to naturally recover?
            if scenario.truth.expected_natural_recovery:
                outcome["is_success"] = True
                
        # For simplicity in this synthetic simulator, we define policy violations
        # as L1 naive strategy ignoring gateway downtime or high-value constraints.
        if decision.action_taken == "CREATE_PAYMENT_LINK":
            if scenario.evidence.gateway_downtime_active or scenario.evidence.opportunity_amount.amount_minor > 40000_00 or scenario.evidence.failure_code == "fraud_suspected":
                # Only L3 correctly enforces policy through PolicyEngine. 
                # L2 has it hardcoded. L1 will violate this.
                if decision.recommendation_source == "L1_STATIC":
                    outcome["is_policy_violation"] = True
                    
        return outcome

class Evaluator:
    def __init__(self, simulator: OutcomeSimulator = None):
        self.simulator = simulator or OutcomeSimulator()

    def evaluate(self, strategy: EvaluationStrategy, scenarios: list[SyntheticScenario]) -> EvaluationMetrics:
        metrics = EvaluationMetrics()
        
        for scenario in scenarios:
            # 1. Provide ONLY observable evidence to the strategy
            decision = strategy.evaluate(scenario.evidence)
            
            amount = Decimal(scenario.evidence.opportunity_amount.amount_minor) / Decimal(100)
            metrics.eligible_cases += 1
            metrics.amount_at_risk += amount
            
            # Record expected recovery value
            if decision.action_taken == "CREATE_PAYMENT_LINK":
                metrics.expected_recovery_value += amount * Decimal(str(decision.probability))
            
            # 2. Simulate outcome using the hidden truth
            outcome = self.simulator.simulate(scenario, decision)
            
            # 3. Decision Quality vs Oracle
            if decision.action_taken == scenario.oracle.expected_decision:
                metrics.correct_decisions += 1
                
            # 4. Metrics Aggregation
            if outcome["is_success"]:
                metrics.successful_verified_recoveries += 1
                metrics.gross_recovered_value += amount
                
            if decision.action_taken == "CREATE_PAYMENT_LINK":
                metrics.interventions += 1
                if outcome["is_failed_intervention"]:
                    metrics.failed_interventions += 1
            elif decision.action_taken == "ESCALATE":
                metrics.escalations += 1
            elif decision.action_taken == "SUPPRESS" or decision.action_taken == "DENY":
                metrics.suppressions += 1
            elif decision.action_taken == "WAIT":
                metrics.waits += 1
                
            if outcome["is_policy_violation"]:
                metrics.policy_violations += 1
            if outcome["is_stopping_rule_violation"]:
                metrics.stopping_rule_violations += 1
            if outcome["is_false_recovery"]:
                metrics.false_recovery_claims += 1

        return metrics
