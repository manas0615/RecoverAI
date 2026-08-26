import pytest

from recoverai.domain.money import CurrencyCode, Money, RevenueAmount


def test_money_construction():
    m = Money(10050, CurrencyCode.INR)
    assert m.amount_minor == 10050
    assert m.currency == CurrencyCode.INR


def test_money_rejects_floats():
    with pytest.raises(TypeError, match="amount_minor cannot be a float"):
        Money(100.50, CurrencyCode.INR)


def test_money_rejects_invalid_types():
    with pytest.raises(TypeError):
        Money("100", CurrencyCode.INR)
    with pytest.raises(TypeError):
        Money(100, "INR")


def test_money_arithmetic():
    m1 = Money(1000, CurrencyCode.INR)
    m2 = Money(500, CurrencyCode.INR)

    assert m1 + m2 == Money(1500, CurrencyCode.INR)
    assert m1 - m2 == Money(500, CurrencyCode.INR)


def test_money_currency_mismatch():
    m1 = Money(1000, CurrencyCode.INR)
    m2 = Money(500, CurrencyCode.USD)

    with pytest.raises(ValueError, match="Currency mismatch"):
        _ = m1 + m2

    with pytest.raises(ValueError, match="Currency mismatch"):
        _ = m1 - m2


def test_money_equality():
    m1 = Money(1000, CurrencyCode.INR)
    m2 = Money(1000, CurrencyCode.INR)
    m3 = Money(1000, CurrencyCode.USD)
    m4 = Money(2000, CurrencyCode.INR)

    assert m1 == m2
    assert m1 != m3
    assert m1 != m4


def test_revenue_amount_wrapper():
    m = Money(1000, CurrencyCode.INR)
    ra = RevenueAmount(m)
    assert ra.amount_minor == 1000
    assert ra.currency == CurrencyCode.INR


def test_revenue_amount_rejects_negative():
    m = Money(-100, CurrencyCode.INR)
    with pytest.raises(ValueError, match="RevenueAmount cannot be negative"):
        RevenueAmount(m)
