import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

# First, find the def analyze_case block.
# We will just replace it entirely to be safe and accurate.
analyze_block_start = content.find('async def analyze_case')
analyze_block_end = content.find('@app.get("/recovery-cases/{case_id}/timeline"', analyze_block_start)

new_analyze_block = '''async def analyze_case(case_id: str):
    from datetime import UTC, datetime
    from recoverai.domain.audit import AuditActor, AuditActorType, AuditEvent, AuditEventType
    from recoverai.persistence.repositories.audit import AuditRepository
    from recoverai.policy.engine import PolicyContext
    from recoverai.persistence.repositories.action import RecoveryActionRepository
    
    # 1. Start Analysis
    with container.tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)
        audit_repo = AuditRepository(conn)
        try:
            case = case_repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")

        events = [event_repo.get(eid) for eid in case.source_event_ids]
        
        audit_repo.append(
            AuditEvent(
                event_type=AuditEventType.ANALYSIS_STARTED,
                actor=AuditActor(type=AuditActorType.SYSTEM, id="api"),
                case_id=case.case_id,
                timestamp=datetime.now(UTC),
            )
        )

    try:
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
                    },
                )
            )

        # 4. Run Policy
        with container.tm.transaction() as conn:
            action_history = RecoveryActionRepository(conn).get_by_case(case.case_id)
            
        policy_context = PolicyContext(
            merchant_id=case.merchant_id.value,
            customer_id=case.customer_id.value if case.customer_id else None,
        )
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

        # Do NOT auto-execute (as requested by instructions)
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
        }

    except Exception as e:
        import logging
        logging.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
'''

content = content[:analyze_block_start] + new_analyze_block + '\n\n' + content[analyze_block_end:]

with open('recoverai/api/main.py', 'w') as f:
    f.write(content)
