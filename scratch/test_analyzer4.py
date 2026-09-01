import asyncio
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.llm_gateway.engine import LLMGateway
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus
from recoverai.domain.money import RevenueAmount, Money, CurrencyCode
from recoverai.domain.event import RevenueEvent
from datetime import datetime, UTC
import logging
logging.basicConfig(level=logging.DEBUG)

case = RecoveryCase(
    case_id="case_LIVE",
    customer_id="cust_123",
    amount_at_risk=RevenueAmount(Money(10000, CurrencyCode.INR)),
    status=RecoveryCaseStatus.OPEN
)

gateway = LLMGateway(GatewayConfig.from_env())
try:
    candidates = gateway.generate_intervention_candidates(case, [], {}, None)
    print("Candidates:", candidates)
except Exception as e:
    print(f"Gateway failed: {e}")
