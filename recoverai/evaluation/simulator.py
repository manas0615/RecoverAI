import random
from dataclasses import dataclass

from recoverai.domain.money import CurrencyCode, Money


@dataclass
class ObservableCaseEvidence:
    scenario_id: str
    merchant_id: str
    customer_id: str
    opportunity_amount: Money
    failure_code: str
    gateway_downtime_active: bool
    historical_failure_count: int


@dataclass
class HiddenOutcomeTruth:
    receptive_to_intervention: bool
    expected_natural_recovery: bool
    provider_error_on_execution: bool


@dataclass
class EvaluationOracle:
    expected_decision: str


@dataclass
class SyntheticScenario:
    evidence: ObservableCaseEvidence
    truth: HiddenOutcomeTruth
    oracle: EvaluationOracle


class SyntheticScenarioGenerator:
    def __init__(
        self,
        seed: int = 42,
        prob_systemic: float = 0.10,
        prob_receptive: float = 0.60,
        prob_natural_recovery: float = 0.15,
        prob_provider_error: float = 0.05,
    ):
        self._seed = seed
        self._rng = random.Random(self._seed)
        self._counter = 0
        self.prob_systemic = prob_systemic
        self.prob_receptive = prob_receptive
        self.prob_natural_recovery = prob_natural_recovery
        self.prob_provider_error = prob_provider_error

    def _determine_oracle_decision(
        self, evidence: ObservableCaseEvidence, truth: HiddenOutcomeTruth
    ) -> str:
        """
        Independent oracle rules defining the benchmark's expected ideal decision.
        It uses both observable evidence and hidden scenario truth to determine
        what SHOULD happen, entirely independently of L2 or P-Engine.
        """
        if evidence.failure_code == "fraud_suspected":
            return "DENY"
        if evidence.gateway_downtime_active:
            return "WAIT"
        if truth.expected_natural_recovery:
            # Wasteful to intervene if it recovers naturally
            return "SUPPRESS"
        if not truth.receptive_to_intervention:
            # Will fail anyway, don't waste execution limits
            return "SUPPRESS"
        if evidence.opportunity_amount.amount_minor >= 45000_00:
            return "ESCALATE"
            
        return "CREATE_PAYMENT_LINK"

    def generate(self, count: int) -> list[SyntheticScenario]:
        scenarios = []
        for i in range(count):
            self._counter += 1

            is_degraded = self._rng.random() < self.prob_systemic
            is_receptive = self._rng.random() < self.prob_receptive
            is_high_value = self._rng.random() < 0.05
            is_repeated_failure = self._rng.random() < 0.20
            is_provider_error = self._rng.random() < self.prob_provider_error

            if is_high_value:
                amount_minor = self._rng.randint(10000_00, 50000_00)
            else:
                amount_minor = self._rng.randint(100_00, 5000_00)

            if is_degraded:
                cause = "system_downtime"
            elif is_repeated_failure:
                cause = "insufficient_funds"
            else:
                cause = self._rng.choice(
                    ["customer_error", "network_timeout", "fraud_suspected"]
                )

            historical_count = (
                self._rng.randint(2, 5)
                if is_repeated_failure
                else self._rng.randint(0, 1)
            )

            if is_receptive and not is_degraded:
                expected_natural_recovery = (
                    self._rng.random() < self.prob_natural_recovery
                )
            else:
                expected_natural_recovery = False

            evidence = ObservableCaseEvidence(
                scenario_id=f"sim_{self._counter}",
                merchant_id=f"M_{self._rng.randint(1, 10)}",
                customer_id=f"C_{self._rng.randint(1, 1000)}",
                opportunity_amount=Money(
                    amount_minor=amount_minor, currency=CurrencyCode.INR
                ),
                failure_code=cause,
                gateway_downtime_active=is_degraded,
                historical_failure_count=historical_count,
            )
            
            truth = HiddenOutcomeTruth(
                receptive_to_intervention=is_receptive,
                expected_natural_recovery=expected_natural_recovery,
                provider_error_on_execution=is_provider_error
            )
            
            oracle = EvaluationOracle(
                expected_decision=self._determine_oracle_decision(evidence, truth)
            )
            
            scenarios.append(SyntheticScenario(evidence=evidence, truth=truth, oracle=oracle))
        return scenarios
