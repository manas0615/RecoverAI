from recoverai.api.main import container
from datetime import datetime, UTC
from recoverai.domain.identifiers import RecoveryCaseId
with container.tm.transaction() as conn:
    from recoverai.persistence.repositories.case import RecoveryCaseRepository
    case_repo = RecoveryCaseRepository(conn)
    case = case_repo.get(RecoveryCaseId("case_TXDBvr4RrbgdC8"))
    if case:
        container.verification.reconcile_case(case, datetime.now(UTC))
        print("Verified case")
