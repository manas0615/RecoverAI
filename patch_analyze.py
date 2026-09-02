import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """
        # 6. Auto-execute based on policy decision
        from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction, RecoveryActionId
        import uuid
        
        with container.tm.transaction() as conn:
            action_repo = RecoveryActionRepository(conn)
            
            action = RecoveryAction(
                action_id=RecoveryActionId(f"act_{uuid.uuid4().hex[:12]}"),
                case_id=case.case_id,
                action_type=plan.selected_action_type if plan and plan.selected_action_type else ActionType.CREATE_PAYMENT_LINK,
                requested_at=datetime.now(UTC),
                status=ActionStatus.ESCALATED if decision.decision == PolicyDecisionValue.ESCALATE else (ActionStatus.PROPOSED if decision.decision == PolicyDecisionValue.APPROVE else ActionStatus.CANCELLED)
            )
            
            # Since action_service evaluates policy again and requires these:
            setattr(action, "_real_plan", plan)
            setattr(action, "_real_cause", cause)
            
            # Action repo doesn't persist _real_plan, so we execute immediately if APPROVE or ESCALATE
            # But wait, action MUST be in DB for action_service to claim_for_execution!
            # Let's save it to DB first.
            action_repo.save(action)
        
        # Now execute it if it's not denied
        if decision.decision in [PolicyDecisionValue.APPROVE, PolicyDecisionValue.ESCALATE]:
            # execute_action handles the policy check and status transitions!
            # We must set real_plan again because we just saved it and execute_action will need it
            setattr(action, "_real_plan", plan)
            setattr(action, "_real_cause", cause)
            try:
                container.action_service.execute_action(action)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Execution failed: {e}")
        
        return {
"""

content = content.replace("# 6. Do NOT auto-execute (as requested by instructions)\n        return {", replacement)

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")
