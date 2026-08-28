from dataclasses import dataclass

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
    # In a full app, this would also have dependencies to n8n, Verification, Intelligence etc.
    # We pass placeholders or just rely on DB for Read tools.
    # intelligence: Any
