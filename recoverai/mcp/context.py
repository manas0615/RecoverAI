from dataclasses import dataclass
from typing import Any

from recoverai.integrations.razorpay.service import RazorpayExecutionService
from recoverai.persistence.connection import TransactionManager
from recoverai.policy.engine import PolicyEngine
from recoverai.state_machine.engine import RecoveryStateMachine


@dataclass
class MCPContext:
    tm: TransactionManager
    state_machine: RecoveryStateMachine
    policy_engine: PolicyEngine
    razorpay_service: RazorpayExecutionService
    action_service: Any
    intelligence: Any
