from recoverai.api.main import container
from datetime import datetime, UTC
from recoverai.domain.identifiers import RecoveryCaseId

case_repo = container.verification.case_repo
case = case_repo.get(RecoveryCaseId("case_TXDBvr4RrbgdC8"))
container.verification.reconcile_case(case, datetime.now(UTC))
case_repo.conn.commit()
print("Committed")
