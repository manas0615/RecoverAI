from recoverai.api.main import container
from datetime import datetime, UTC
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.domain.case import CaseWorkflowState
with container.tm.transaction() as conn:
    from recoverai.persistence.repositories.case import RecoveryCaseRepository
    case_repo = RecoveryCaseRepository(conn)
    case = case_repo.get(RecoveryCaseId("case_TXDBvr4RrbgdC8"))
    if case:
        case.advance_workflow(CaseWorkflowState.VERIFYING, datetime.now(UTC))
        case_repo.save(case)
        print("Set to VERIFYING")
