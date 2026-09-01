import asyncio
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.llm_gateway.engine import LLMGateway
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus
from recoverai.domain.money import RevenueAmount, Money, CurrencyCode
from recoverai.domain.event import RevenueEvent
from datetime import datetime, UTC

case = RecoveryCase(
    case_id="case_LIVE",
    customer_id="cust_123",
    amount_at_risk=RevenueAmount(Money(10000, CurrencyCode.INR)),
    status=RecoveryCaseStatus.OPEN,
    created_at=datetime.now(UTC),
    updated_at=datetime.now(UTC)
)

analyzer = RevenueIntelligenceAnalyzer(LLMGateway(GatewayConfig.from_env()))
# run analyzer.analyze
result = analyzer.analyze(case, {"customer_failure_count": 1}, [])
print(result[2].selection_model_version)
print(result[2].selected_action_type)
