from dataclasses import dataclass

from recoverai.domain.money import CurrencyCode, Money


@dataclass
class SyntheticScenario:
    scenario_id: str
    merchant_id: str
    customer_id: str
    opportunity_amount: Money
    true_failure_cause: str
    receptive_to_intervention: bool
    systemic_degradation_active: bool

    # Ground Truth expected outcomes
    expected_optimal_action: str | None
    expected_natural_recovery: bool


class SyntheticScenarioGenerator:
    def __init__(self, seed: int = 42):
        self._seed = seed
        self._counter = 0

    def generate(self, count: int) -> list[SyntheticScenario]:
        scenarios = []
        for i in range(count):
            self._counter += 1
            is_degraded = self._counter % 10 == 0
            is_receptive = self._counter % 3 != 0
            amount_minor = 150000 + (self._counter * 1000)

            scenarios.append(
                SyntheticScenario(
                    scenario_id=f"sim_{self._counter}",
                    merchant_id=f"M_{self._counter % 5}",
                    customer_id=f"C_{self._counter}",
                    opportunity_amount=Money(
                        amount_minor=amount_minor, currency=CurrencyCode.INR
                    ),
                    true_failure_cause="customer_error"
                    if not is_degraded
                    else "system_downtime",
                    receptive_to_intervention=is_receptive,
                    systemic_degradation_active=is_degraded,
                    expected_optimal_action="CREATE_PAYMENT_LINK"
                    if is_receptive and not is_degraded
                    else ("SUPPRESS" if is_degraded else None),
                    expected_natural_recovery=False,
                )
            )
        return scenarios
