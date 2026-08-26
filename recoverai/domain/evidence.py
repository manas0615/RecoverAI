from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Probability:
    """
    Represents a probability value between 0.0 and 1.0.
    """

    value: float
    meaning: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, float):
            raise TypeError("Probability value must be a float")
        # Ensure it's not NaN or Infinity (since math.isnan requires math module, can just use check)
        import math

        if math.isnan(self.value) or math.isinf(self.value):
            raise ValueError("Probability value cannot be NaN or Infinity")
        if not (0.0 <= self.value <= 1.0):
            raise ValueError("Probability value must be between 0.0 and 1.0")
        if not self.meaning or not self.meaning.strip():
            raise ValueError("Probability meaning must be provided")


class EvidenceSourceType(Enum):
    RAZORPAY_EVENT = "RAZORPAY_EVENT"
    RAZORPAY_PAYMENT = "RAZORPAY_PAYMENT"
    RAZORPAY_ORDER = "RAZORPAY_ORDER"
    PAYMENT_LINK = "PAYMENT_LINK"
    MERCHANT_EVENT = "MERCHANT_EVENT"
    CUSTOMER_HISTORY = "CUSTOMER_HISTORY"
    MODEL_SIGNAL = "MODEL_SIGNAL"
    SIMULATION_EVENT = "SIMULATION_EVENT"


@dataclass(frozen=True)
class EvidenceReference:
    """
    Identifies an observation (fact) used by a prediction or decision.
    Distinguished from AI interpretations.
    """

    source_type: EvidenceSourceType
    source_id: str
    observed_at: datetime
    field: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_type, EvidenceSourceType):
            raise TypeError("source_type must be an EvidenceSourceType")
        if not self.source_id.strip():
            raise ValueError("source_id cannot be empty")
        if not self.observed_at.tzinfo:
            raise ValueError("observed_at timestamp must be timezone-aware")
