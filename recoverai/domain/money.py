from dataclasses import dataclass
from enum import Enum


class CurrencyCode(Enum):
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


@dataclass(frozen=True)
class Money:
    """
    Represents a monetary quantity in the smallest minor unit.
    For INR, 100.50 is represented as 10050.
    """

    amount_minor: int
    currency: CurrencyCode

    def __post_init__(self) -> None:
        if isinstance(self.amount_minor, float):
            raise TypeError("amount_minor cannot be a float")
        if not isinstance(self.amount_minor, int) or isinstance(
            self.amount_minor, bool
        ):
            raise TypeError("amount_minor must be an integer")
        if not isinstance(self.currency, CurrencyCode):
            raise TypeError("currency must be a CurrencyCode enum")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} != {other.currency}")
        return Money(self.amount_minor + other.amount_minor, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} != {other.currency}")
        return Money(self.amount_minor - other.amount_minor, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return (
            self.amount_minor == other.amount_minor and self.currency == other.currency
        )


@dataclass(frozen=True)
class RevenueAmount:
    """
    Semantic wrapper around Money for amounts associated with revenue opportunity.
    Must not be negative.
    """

    money: Money

    def __post_init__(self) -> None:
        if not isinstance(self.money, Money):
            raise TypeError("RevenueAmount must wrap a Money object")
        if self.money.amount_minor < 0:
            raise ValueError("RevenueAmount cannot be negative")

    @property
    def amount_minor(self) -> int:
        return self.money.amount_minor

    @property
    def currency(self) -> CurrencyCode:
        return self.money.currency
