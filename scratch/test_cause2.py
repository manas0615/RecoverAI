from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus
from recoverai.domain.money import RevenueAmount, Money, CurrencyCode
import datetime

config = GatewayConfig.from_env()
gateway = ConcreteLLMGateway(config)

case = RecoveryCase(
    case_id="case_LIVE",
    customer_id="cust_123",
    amount_at_risk=RevenueAmount(Money(10000, CurrencyCode.INR)),
    status=RecoveryCaseStatus.OPEN
)

try:
    cause = gateway.synthesize_cause(case, [], {})
    print("CAUSE CATEGORY:", cause.category)
    print("CAUSE CONFIDENCE:", cause.confidence.value)
except Exception as e:
    print(e)

