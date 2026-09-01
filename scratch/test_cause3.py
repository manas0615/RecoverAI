from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus, RecoveryCaseId, MerchantId, RevenueSource
from recoverai.domain.money import RevenueAmount, Money, CurrencyCode
import datetime

config = GatewayConfig.from_env()
gateway = ConcreteLLMGateway(config)

case = RecoveryCase(
    case_id=RecoveryCaseId("case_LIVE"),
    merchant_id=MerchantId("m1"),
    revenue_source=RevenueSource.PAYMENT_LINK,
    opened_at=datetime.datetime.now(datetime.UTC),
    source_event_ids=["evt_LIVE"],
    customer_id="cust_123",
    amount_at_risk=RevenueAmount(Money(10000, CurrencyCode.INR)),
    status=RecoveryCaseStatus.OPEN
)

try:
    cause = gateway.synthesize_cause(case, [], {})
    print("CAUSE CATEGORY:", cause.category)
    print("CAUSE CONFIDENCE:", cause.confidence.value)
except Exception as e:
    import traceback
    traceback.print_exc()

