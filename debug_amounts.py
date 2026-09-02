from recoverai.api.main import container
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.action import RecoveryActionRepository

with container.tm.transaction() as conn:
    case_repo = RecoveryCaseRepository(conn)
    action_repo = RecoveryActionRepository(conn)
    
    for case_id_str in ["case_ev_1963cb039253", "case_ev_d1a21ce2f3e4"]:
        case_id = RecoveryCaseId(case_id_str)
        case = case_repo.get(case_id)
        if case:
            print(f"Case {case_id_str}: amount_at_risk={case.amount_at_risk.amount_minor}")
            actions = action_repo.get_by_case(case_id)
            for a in actions:
                print(f"  Action {a.action_id.value}: plan_snapshot={a.plan_snapshot}")
