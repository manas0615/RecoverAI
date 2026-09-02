with open("scripts/seed_demo_data.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'action_id=RecoveryActionId("act_ESCALATION"),\n            case_id=case_e.case_id,\n            action_type=ActionType.CREATE_PAYMENT_LINK,\n            status=ActionStatus.PROPOSED,',
    'action_id=RecoveryActionId("act_ESCALATION"),\n            case_id=case_e.case_id,\n            action_type=ActionType.CREATE_PAYMENT_LINK,\n            status=ActionStatus.ESCALATED,'
)

with open("scripts/seed_demo_data.py", "w", encoding="utf-8") as f:
    f.write(content)
