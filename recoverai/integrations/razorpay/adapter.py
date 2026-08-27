import base64
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum

from recoverai.domain.action import ActionType, RecoveryAction
from recoverai.domain.case import RecoveryCase
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue

logger = logging.getLogger(__name__)


class RazorpayExecutionResultType(Enum):
    SUCCESSFUL_REQUEST = "SUCCESSFUL_REQUEST"
    FAILED_BEFORE_SEND = "FAILED_BEFORE_SEND"
    PROVIDER_REJECTED = "PROVIDER_REJECTED"
    TIMEOUT_UNKNOWN = "TIMEOUT_UNKNOWN"
    NETWORK_UNKNOWN = "NETWORK_UNKNOWN"


@dataclass
class RazorpayExecutionResult:
    result_type: RazorpayExecutionResultType
    provider_reference: str | None = None
    short_url: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class RazorpayConfig:
    key_id: str
    key_secret: str
    mode: str = "test"
    timeout_seconds: float = 10.0


class RazorpayAdapter:
    def __init__(self, config: RazorpayConfig) -> None:
        self.config = config

    def execute_payment_link(
        self, action: RecoveryAction, case: RecoveryCase, decision: PolicyDecision
    ) -> RazorpayExecutionResult:
        logger.info(
            "execution_started",
            extra={
                "action_id": action.action_id.value,
                "case_id": case.case_id.value,
            },
        )

        if self.config.mode != "test":
            logger.error("Attempted to execute in non-test mode.")
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
                error_message="Test mode is required for execution",
            )

        if decision.decision != PolicyDecisionValue.APPROVE:
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
                error_message="Action not approved by policy",
            )

        if decision.case_id != action.case_id:
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
                error_message="Policy decision case ID does not match action case ID",
            )

        if action.action_type != ActionType.CREATE_PAYMENT_LINK:
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
                error_message="Action type is not CREATE_PAYMENT_LINK",
            )

        reference_id = action.action_id.value
        if len(reference_id) > 40:
            import hashlib

            h = hashlib.sha256(reference_id.encode("utf-8")).hexdigest()[:8]
            reference_id = reference_id[:31] + "_" + h

        payload = {
            "amount": case.amount_at_risk.amount_minor,
            "currency": case.amount_at_risk.currency.value,
            "reference_id": reference_id,
            "description": f"Recovery Payment for case {case.case_id.value}",
        }

        url = "https://api.razorpay.com/v1/payment_links"
        data = json.dumps(payload).encode("utf-8")

        auth_str = f"{self.config.key_id}:{self.config.key_secret}"
        auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_bytes}",
            },
            method="POST",
        )

        logger.info(
            "provider_request_sent",
            extra={
                "action_id": action.action_id.value,
                "case_id": case.case_id.value,
                "reference_id": reference_id,
            },
        )

        try:
            with urllib.request.urlopen(
                req, timeout=self.config.timeout_seconds
            ) as response:
                response_data = json.loads(response.read().decode("utf-8"))

                logger.info(
                    "provider_response_received",
                    extra={
                        "action_id": action.action_id.value,
                        "case_id": case.case_id.value,
                        "provider_reference": response_data.get("id"),
                    },
                )

                return RazorpayExecutionResult(
                    result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
                    provider_reference=response_data.get("id"),
                    short_url=response_data.get("short_url"),
                )
        except urllib.error.HTTPError as e:
            logger.info(
                "provider_rejected",
                extra={
                    "action_id": action.action_id.value,
                    "case_id": case.case_id.value,
                    "http_status": e.code,
                },
            )
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.PROVIDER_REJECTED,
                error_message=f"HTTP {e.code}",
            )
        except TimeoutError:
            logger.warning(
                "execution_unknown",
                extra={
                    "action_id": action.action_id.value,
                    "case_id": case.case_id.value,
                    "reason": "timeout",
                },
            )
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
                error_message="Request timed out",
            )
        except urllib.error.URLError as e:
            if (
                isinstance(e.reason, TimeoutError)
                or "timed out" in str(e.reason).lower()
            ):
                logger.warning(
                    "execution_unknown",
                    extra={
                        "action_id": action.action_id.value,
                        "case_id": case.case_id.value,
                        "reason": "timeout",
                    },
                )
                return RazorpayExecutionResult(
                    result_type=RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
                    error_message="Request timed out",
                )

            logger.warning(
                "execution_unknown",
                extra={
                    "action_id": action.action_id.value,
                    "case_id": case.case_id.value,
                    "reason": "network_failure",
                },
            )
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.NETWORK_UNKNOWN,
                error_message=str(e.reason),
            )
        except ValueError as e:
            logger.warning(
                "execution_unknown",
                extra={
                    "action_id": action.action_id.value,
                    "case_id": case.case_id.value,
                    "reason": "unexpected_error",
                },
            )
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.NETWORK_UNKNOWN,
                error_message=str(e),
            )
