import importlib
import urllib.request
from datetime import UTC, datetime

import pytest

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.identifiers import (
    MerchantId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue
from recoverai.integrations.razorpay.adapter import (
    RazorpayAdapter,
    RazorpayConfig,
)


def test_ordinary_pytest_blocked_from_real_provider(monkeypatch):
    monkeypatch.delenv("ALLOW_REAL_RAZORPAY", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "test")

    # Remove any global mock of urlopen to prove the barrier works
    import urllib.request as orig_urllib_request

    importlib.reload(orig_urllib_request)

    # But wait, reload might not undo monkeypatch.setattr
    # Let's just use monkeypatch.undo() for this specific attr or set it to a real function
    def fake_real_urlopen(*args, **kwargs):
        pass  # we should never reach here anyway because of the RuntimeError

    monkeypatch.setattr(urllib.request, "urlopen", fake_real_urlopen)

    config = RazorpayConfig(key_id="test_key", key_secret="test_secret", mode="test")
    adapter = RazorpayAdapter(config)

    case = RecoveryCase(
        case_id=RecoveryCaseId("case_test_iso"),
        merchant_id=MerchantId("merch_demo"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("ev_123")},
    )

    action = RecoveryAction(
        action_id=RecoveryActionId("act_test_iso"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.PROPOSED,
        requested_at=datetime.now(UTC),
    )

    decision = PolicyDecision(
        policy_decision_id=PolicyDecisionId("dec_123"),
        action_id_or_proposal_id="act_test_iso",
        case_id=case.case_id,
        decision=PolicyDecisionValue.APPROVE,
        reason_codes=["TEST_APPROVE"],
        policy_version="1.0",
        evaluated_at=datetime.now(UTC),
    )

    with pytest.raises(
        RuntimeError,
        match="Real Razorpay provider access is disabled during automated tests",
    ):
        adapter.execute_payment_link(action, case, decision)
