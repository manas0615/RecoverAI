import re

with open("recoverai/application/action_service.py", "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace:
#                 decision.decision = PolicyDecisionValue.APPROVE  # type: ignore
#                 decision.matched_rules.append("HUMAN_APPROVAL_OVERRIDE")
#                 decision.reason_codes.append("HUMAN_APPROVAL_OVERRIDE")
# With creating a new object, but wait, dataclasses with replace:
# from dataclasses import replace
# decision = replace(decision, decision=PolicyDecisionValue.APPROVE, matched_rules=decision.matched_rules + ["HUMAN_APPROVAL_OVERRIDE"], reason_codes=decision.reason_codes + ["HUMAN_APPROVAL_OVERRIDE"])

new_code = """                from dataclasses import replace
                decision = replace(
                    decision,
                    decision=PolicyDecisionValue.APPROVE,
                    matched_rules=decision.matched_rules + ["HUMAN_APPROVAL_OVERRIDE"],
                    reason_codes=decision.reason_codes + ["HUMAN_APPROVAL_OVERRIDE"]
                )"""

content = content.replace(
    '                decision.decision = PolicyDecisionValue.APPROVE  # type: ignore\n'
    '                decision.matched_rules.append("HUMAN_APPROVAL_OVERRIDE")\n'
    '                decision.reason_codes.append("HUMAN_APPROVAL_OVERRIDE")',
    new_code
)

with open("recoverai/application/action_service.py", "w", encoding="utf-8") as f:
    f.write(content)
