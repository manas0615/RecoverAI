from recoverai.api.main import container
from datetime import datetime, UTC
from recoverai.domain.identifiers import RecoveryCaseId
with container.tm.transaction() as conn:
    from recoverai.persistence.repositories.case import RecoveryCaseRepository
    from recoverai.persistence.repositories.action import RecoveryActionRepository
    case_repo = RecoveryCaseRepository(conn)
    action_repo = RecoveryActionRepository(conn)
    case = case_repo.get(RecoveryCaseId("case_TXDBvr4RrbgdC8"))
    actions = action_repo.get_pending_verification(case.case_id)
    for action in actions:
        print(action.status.name, action.external_reference, action.failure_reason)
