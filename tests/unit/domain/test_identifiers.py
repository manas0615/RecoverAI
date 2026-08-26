import pytest

from recoverai.domain.identifiers import (
    CustomerId,
    MerchantId,
    RevenueEventId,
)


def test_identifier_valid_construction():
    m = MerchantId("merch_123")
    assert m.value == "merch_123"
    assert str(m) == "merch_123"


def test_identifier_rejects_empty():
    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        MerchantId("")
    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        CustomerId("   ")


def test_identifier_rejects_non_string():
    with pytest.raises(TypeError, match="must be a string"):
        RevenueEventId(123)


def test_identifier_type_separation():
    # Identifiers are distinct types but Python's equality relies on fields unless we check types.
    # Dataclasses will compare equal if their fields are equal.
    # We should ensure that MerchantId("123") != CustomerId("123")
    m = MerchantId("123")
    c = CustomerId("123")
    assert m != c
