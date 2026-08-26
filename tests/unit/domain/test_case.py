from datetime import UTC, datetime

import pytest

from recoverai.domain.case import (
    RecoveryCase,
    RecoveryCaseStatus,
    RecoveryOutcomeValue,
    RevenueSource,
)
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount


def test_recovery_case_valid_construction():
    now = datetime.now(UTC)
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")},
    )
    assert case.status == RecoveryCaseStatus.OPEN


def test_recovery_case_requires_source_event():
    now = datetime.now(UTC)
    with pytest.raises(ValueError, match="must reference at least one source event"):
        RecoveryCase(
            case_id=RecoveryCaseId("case_1"),
            merchant_id=MerchantId("m_1"),
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
            opened_at=now,
            source_event_ids=set(),
        )


def test_recovery_case_add_event():
    now = datetime.now(UTC)
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")},
    )

    case.add_source_event(RevenueEventId("evt_2"), now)
    assert RevenueEventId("evt_2") in case.source_event_ids


def test_recovery_case_close_requires_amount_when_recovered():
    now = datetime.now(UTC)
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")},
    )

    with pytest.raises(
        ValueError, match="RECOVERED outcome requires a recovered_amount"
    ):
        case.close(RecoveryOutcomeValue.RECOVERED, now)

    case.close(
        RecoveryOutcomeValue.RECOVERED,
        now,
        recovered_amount=RevenueAmount(Money(5000, CurrencyCode.INR)),
    )
    assert case.status == RecoveryCaseStatus.CLOSED
    assert case.outcome_type == RecoveryOutcomeValue.RECOVERED


def test_recovery_case_cannot_modify_closed():
    now = datetime.now(UTC)
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")},
    )
    case.close(RecoveryOutcomeValue.NOT_RECOVERED, now)

    with pytest.raises(ValueError, match="Cannot modify a closed RecoveryCase"):
        case.add_source_event(RevenueEventId("evt_2"), now)
