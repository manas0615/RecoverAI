import re

with open('recoverai/policy/engine.py', 'r') as f:
    text = f.read()

replacement = '''        # 4. DEFAULT APPROVAL / ACTION ROUTING
        # ---------------------------------------------------------------------
        if proposed_action_type == ActionType.ESCALATE:
            return self._build_decision(
                context, case, plan, PolicyDecisionValue.ESCALATE, "AI_RECOMMENDED_ESCALATION"
            )

        return self._build_decision(
            context, case, plan, PolicyDecisionValue.APPROVE, "POLICY_APPROVED"
        )'''

text = re.sub(r'# 4\. DEFAULT APPROVAL\s*# -+\s*return self\._build_decision\(\s*context, case, plan, PolicyDecisionValue\.APPROVE, "POLICY_APPROVED"\s*\)', replacement, text)

with open('recoverai/policy/engine.py', 'w') as f:
    f.write(text)

