import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

target_start = content.find('    try:\n        from datetime import UTC, datetime')
target_end = content.find('raise HTTPException(status_code=500, detail="Analysis unavailable")') + len('raise HTTPException(status_code=500, detail="Analysis unavailable")')

new_try_block = '''    try:
        from datetime import UTC, datetime

        from recoverai.domain.audit import (
            AuditActor,
            AuditActorType,
            AuditEvent,
            AuditEventType,
        )
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.policy.engine import PolicyContext
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        
        # 1. Start Analysis
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ANALYSIS_STARTED,
                    actor=AuditActor(type=AuditActorType.SYSTEM, id="api"),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                )
            )

        # 2. Run Intelligence (Outside transaction so frontend can poll)
        risk, cause, plan = container.intelligence.analyze(case, events)

        # 3. Commit LLM Recommendation
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.LLM_RECOMMENDATION_CREATED,
                    actor=AuditActor(type=AuditActorType.LLM_AGENT, id=risk.model_name),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                    metadata={
                        "recommended_action": plan.selected_action_type.value
                        if plan and plan.selected_action_type
                        else "UNKNOWN",
                        "reasoning": plan.selection_reason
                        if plan
                        else "Analysis completed without forming an intervention plan.",
                        "confidence": cause.confidence.value if cause else None,
                        "cause_category": cause.category if cause else None,
                        "recovery_probability": risk.recovery_probability.value
                        if risk
                        else 0.0,
                        "expected_recovery_amount": plan.expected_recovery_value.amount_minor
                        if plan and plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.amount_minor
                            if risk and risk.expected_recovery_value
                            else 0
                        ),
                        "expected_recovery_currency": plan.expected_recovery_value.currency.value
                        if plan and plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.currency.value
                            if risk and risk.expected_recovery_value
                            else "INR"
                        ),
                        "analysis_source": "Gemini"
                        if (cause and cause.analysis_type.name == "LLM")
                        else "Deterministic Fallback",
                        "deterministic_fallback": cause.analysis_type.name != "LLM"
                        if cause
                        else True,
                        "probability_meaning": getattr(
                            risk.recovery_probability,
                            "reasoning",
                            "Derived from historical failure count and systemic signals",
                        )
                        if risk
                        else "No risk assessment available",
                        "model_version": risk.model_version if risk else "UNKNOWN",
                    },
                )
            )

        # 4. Evaluate Policy
        policy_context = PolicyContext(
            policy_version="1.0", current_time=datetime.now(UTC)
        )
        with container.tm.transaction() as conn:
            action_history = RecoveryActionRepository(conn).get_by_case(case.case_id)
            
        decision = container.policy.evaluate(
            policy_context, case, plan, action_history, cause=cause
        )

        # 5. Commit Policy Decision
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.POLICY_DECISION_CREATED,
                    actor=AuditActor(type=AuditActorType.POLICY_ENGINE, id="policy"),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                    metadata={
                        "decision": decision.decision.value,
                        "reasons": decision.reason_codes,
                        "decision_reason": ", ".join(decision.reason_codes),
                    },
                )
            )

        # 6. Do NOT auto-execute (as requested by instructions)
        return {
            "status": "success",
            "recommendation": plan.selected_action_type.value
            if plan and plan.selected_action_type
            else "UNKNOWN",
            "recommendation_reason": plan.selection_reason
            if plan
            else "Analysis completed without forming an intervention plan.",
            "expected_recovery_value": plan.expected_recovery_value.amount_minor
            if plan and plan.expected_recovery_value
            else (
                risk.expected_recovery_value.amount_minor
                if risk and risk.expected_recovery_value
                else 0
            ),
            "recovery_probability": risk.recovery_probability.value
            if risk
            else 0.0,
            "probability_meaning": getattr(
                risk.recovery_probability,
                "reasoning",
                "Derived from historical failure count and systemic signals",
            )
            if risk
            else "No risk assessment available",
            "cause_category": cause.category if cause else "UNKNOWN",
            "cause_confidence": cause.confidence.value if cause else 0.0,
            "policy_decision": decision.decision.value if decision else "UNKNOWN",
            "policy_reasons": decision.reason_codes if decision else [],
            "model_version": risk.model_version if risk else "UNKNOWN",
        }
    except Exception as e:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).error(f"Analysis failed for {case_id}: {e}")
        raise HTTPException(status_code=500, detail="Analysis unavailable")'''

content = content[:target_start] + new_try_block + content[target_end:]

guard = '''        if case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")

        events = [event_repo.get(eid) for eid in case.source_event_ids]'''
content = content.replace('        events = [event_repo.get(eid) for eid in case.source_event_ids]', guard)

with open('recoverai/api/main.py', 'w') as f:
    f.write(content)
