import io
import json
import urllib.error
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

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
    RazorpayExecutionResultType,
)


@pytest.fixture
def config() -> RazorpayConfig:
    return RazorpayConfig(key_id="test_key", key_secret="test_secret", mode="test")


@pytest.fixture
def adapter(config: RazorpayConfig) -> RazorpayAdapter:
    return RazorpayAdapter(config)


@pytest.fixture
def base_case() -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )


@pytest.fixture
def valid_action() -> RecoveryAction:
    return RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_1"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=datetime.now(UTC),
        status=ActionStatus.VERIFICATION_PENDING,
    )


@pytest.fixture
def valid_decision() -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id=PolicyDecisionId("pd_1"),
        case_id=RecoveryCaseId("case_1"),
        action_id_or_proposal_id="act_1",
        decision=PolicyDecisionValue.APPROVE,
        policy_version="1.0",
        evaluated_at=datetime.now(UTC),
    )


def test_test_mode_guard(
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    adapter = RazorpayAdapter(RazorpayConfig("key", "secret", mode="live"))
    result = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND
    assert "Test mode is required" in (result.error_message or "")


def test_authorization_guard(
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    from dataclasses import replace

    # Test DENY
    deny_decision = replace(valid_decision, decision=PolicyDecisionValue.DENY)
    result = adapter.execute_payment_link(valid_action, base_case, deny_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test SUPPRESS
    suppress_decision = replace(valid_decision, decision=PolicyDecisionValue.SUPPRESS)
    result = adapter.execute_payment_link(valid_action, base_case, suppress_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test ESCALATE
    escalate_decision = replace(valid_decision, decision=PolicyDecisionValue.ESCALATE)
    result = adapter.execute_payment_link(valid_action, base_case, escalate_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test REVALIDATE
    revalidate_decision = replace(
        valid_decision, decision=PolicyDecisionValue.REVALIDATE
    )
    result = adapter.execute_payment_link(valid_action, base_case, revalidate_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test Case Mismatch
    mismatch_decision = replace(valid_decision, case_id=RecoveryCaseId("case_2"))
    result = adapter.execute_payment_link(valid_action, base_case, mismatch_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test Action Mismatch
    mismatch_action = replace(valid_action, action_type=ActionType.ESCALATE)
    result = adapter.execute_payment_link(mismatch_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

    # Test Missing Decision
    # type checker normally prevents this, but testing runtime guard
    result = adapter.execute_payment_link(valid_action, base_case, None)  # type: ignore
    assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND


@patch("urllib.request.urlopen")
def test_successful_request(
    mock_urlopen: MagicMock,
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    response_data = json.dumps(
        {"id": "plink_123", "short_url": "https://rzp.io/i/123"}
    ).encode("utf-8")
    mock_response = MagicMock()
    mock_response.read.return_value = response_data
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST
    assert result.provider_reference == "plink_123"
    assert result.short_url == "https://rzp.io/i/123"

    # Verify request payload
    request = mock_urlopen.call_args[0][0]
    payload = json.loads(request.data.decode("utf-8"))
    assert payload["amount"] == 5000
    assert payload["currency"] == "INR"
    assert payload["reference_id"] == "act_1"
    assert "Authorization" in request.headers


@patch("urllib.request.urlopen")
def test_provider_rejected(
    mock_urlopen: MagicMock,
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    # Simulate a 400 Bad Request
    from email.message import Message

    msg = Message()
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "url", 400, "Bad Request", msg, io.BytesIO(b"")
    )
    result = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.PROVIDER_REJECTED
    assert "HTTP 400" in (result.error_message or "")


@patch("urllib.request.urlopen")
def test_timeout_unknown(
    mock_urlopen: MagicMock,
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    # Simulate a network timeout (could be TimeoutError built-in or urllib URLError with TimeoutError)
    mock_urlopen.side_effect = TimeoutError("socket timeout")
    result = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.TIMEOUT_UNKNOWN
    assert mock_urlopen.call_count == 1

    # Simulate URLError with timed out
    mock_urlopen.side_effect = urllib.error.URLError("timed out")
    result2 = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result2.result_type == RazorpayExecutionResultType.TIMEOUT_UNKNOWN
    assert mock_urlopen.call_count == 2


@patch("urllib.request.urlopen")
def test_network_unknown(
    mock_urlopen: MagicMock,
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    # Simulate an arbitrary network connection failure (not a timeout)
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
    result = adapter.execute_payment_link(valid_action, base_case, valid_decision)
    assert result.result_type == RazorpayExecutionResultType.NETWORK_UNKNOWN


@patch("urllib.request.urlopen")
def test_long_reference_id_truncation(
    mock_urlopen: MagicMock,
    adapter: RazorpayAdapter,
    valid_action: RecoveryAction,
    base_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    import json

    long_id_a = "act_1234567890123456789012345678901234567890_A"
    long_id_b = "act_1234567890123456789012345678901234567890_B"

    from dataclasses import replace

    action_a = replace(valid_action, action_id=RecoveryActionId(long_id_a))
    action_b = replace(valid_action, action_id=RecoveryActionId(long_id_b))

    # Needs matching policy decisions
    decision_a = replace(valid_decision, action_id_or_proposal_id=long_id_a)
    decision_b = replace(valid_decision, action_id_or_proposal_id=long_id_b)

    mock_urlopen.return_value.__enter__.return_value.read.return_value = (
        b'{"id": "plink_1"}'
    )

    adapter.execute_payment_link(action_a, base_case, decision_a)
    req_a = mock_urlopen.call_args_list[0][0][0]
    ref_a = json.loads(req_a.data.decode("utf-8"))["reference_id"]

    adapter.execute_payment_link(action_b, base_case, decision_b)
    req_b = mock_urlopen.call_args_list[1][0][0]
    ref_b = json.loads(req_b.data.decode("utf-8"))["reference_id"]

    assert len(ref_a) == 40
    assert len(ref_b) == 40
    assert ref_a != ref_b

    # Same action repeated produces same reference
    adapter.execute_payment_link(action_a, base_case, decision_a)
    req_a2 = mock_urlopen.call_args_list[2][0][0]
    ref_a2 = json.loads(req_a2.data.decode("utf-8"))["reference_id"]
    assert ref_a == ref_a2
