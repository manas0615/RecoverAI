import asyncio
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.llm_gateway.gateway import LLMGateway
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus
from recoverai.domain.money import RevenueAmount, Money, Currency
from recoverai.domain.event import RevenueEvent

case = RecoveryCase(
    case_id="case_LIVE",
    customer_id="cust_123",
    amount_at_risk=RevenueAmount(Money(10000, Currency.INR)),
    status=RecoveryCaseStatus.OPEN
)

analyzer = RevenueIntelligenceAnalyzer(LLMGateway(GatewayConfig.from_env()))
plan = analyzer.analyze(case, {"customer_failure_count": 1}, [])
print(plan)
