from dataclasses import dataclass
from typing import Any
from datetime import datetime

from recoverai.domain.identifiers import RecoveryCaseId, RevenueEventId
from recoverai.domain.money import RevenueAmount
from recoverai.domain.case import RecoveryOutcomeValue

@dataclass(frozen=True)
class Command:
    pass

@dataclass(frozen=True)
class CreateCaseCommand(Command):
    revenue_event_id: RevenueEventId
    timestamp: datetime

@dataclass(frozen=True)
class AddEventToCaseCommand(Command):
    case_id: RecoveryCaseId
    revenue_event_id: RevenueEventId
    timestamp: datetime

@dataclass(frozen=True)
class AssessRiskCommand(Command):
    case_id: RecoveryCaseId
    timestamp: datetime

@dataclass(frozen=True)
class ExecuteActionCommand(Command):
    case_id: RecoveryCaseId
    action_type: str
    timestamp: datetime

@dataclass(frozen=True)
class CloseCaseCommand(Command):
    case_id: RecoveryCaseId
    outcome: RecoveryOutcomeValue
    timestamp: datetime
    recovered_amount: RevenueAmount | None = None
