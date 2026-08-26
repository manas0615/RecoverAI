from abc import ABC, abstractmethod
from typing import Any

from recoverai.domain.assessment import CauseAssessment
from recoverai.domain.case import RecoveryCase
from recoverai.domain.event import RevenueEvent
from recoverai.domain.plan import InterventionCandidate


class LLMGateway(ABC):
    """
    Abstract boundary for provider-agnostic AI capabilities (P10 implementation later).
    Enforces typed, structured outputs without directly importing provider SDKs.
    """

    @abstractmethod
    def synthesize_cause(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
    ) -> CauseAssessment | None:
        """
        Synthesizes a root cause assessment from heterogeneous context.
        Returns None if synthesis fails or is inconclusive.
        """

    @abstractmethod
    def generate_intervention_candidates(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
        cause: CauseAssessment,
    ) -> list[InterventionCandidate]:
        """
        Evaluates potential actions and returns ranked/scored candidates.
        """
