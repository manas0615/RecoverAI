import json
import math
from datetime import UTC, datetime

from recoverai.domain import CurrencyCode, Money, Probability, RevenueAmount


def dt_to_str(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if not dt.tzinfo:
        raise ValueError("Cannot serialize naive datetime")
    # Store as strict UTC ISO string
    return dt.astimezone(UTC).isoformat()


def str_to_dt(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    dt = datetime.fromisoformat(dt_str)
    if not dt.tzinfo:
        raise ValueError(f"Database returned naive datetime string: {dt_str}")
    return dt


def float_to_prob(val: float | None, meaning: str) -> Probability | None:
    if val is None:
        return None
    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"Invalid persisted probability: {val}")
    if val < 0.0 or val > 1.0:
        raise ValueError(f"Probability out of bounds: {val}")
    return Probability(val, meaning)


def prob_to_float(p: Probability | None) -> float | None:
    if not p:
        return None
    return p.value


def row_to_money(amount_minor: int | None, currency: str | None) -> Money | None:
    if amount_minor is None or currency is None:
        return None
    # Will raise ValueError if currency string is invalid for CurrencyCode
    return Money(amount_minor, CurrencyCode(currency))


def row_to_revenue_amount(
    amount_minor: int | None, currency: str | None
) -> RevenueAmount | None:
    m = row_to_money(amount_minor, currency)
    if not m:
        return None
    return RevenueAmount(m)


def safe_json_loads(data: str | None) -> dict | list | None:
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in persistence: {e}")
