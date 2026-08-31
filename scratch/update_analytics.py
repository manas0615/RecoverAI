import re

with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add awaiting_approval and in_execution to get_analytics
old_analytics_init = """        revenue_at_risk = {}
        verified_recovered = {}
        unknown_exposure = {}
        active_cases = 0
        outcome_distribution = {"""
new_analytics_init = """        revenue_at_risk = {}
        verified_recovered = {}
        unknown_exposure = {}
        active_cases = 0
        awaiting_approval = 0
        in_execution_count = 0
        outcome_distribution = {"""
content = content.replace(old_analytics_init, new_analytics_init)

old_analytics_loop = """            if case.status.value == "OPEN":
                revenue_at_risk[curr] += case.amount_at_risk.amount_minor
                active_cases += 1
                unknown_exposure[curr] += case.amount_at_risk.amount_minor"""
new_analytics_loop = """            if case.status.value == "OPEN":
                revenue_at_risk[curr] += case.amount_at_risk.amount_minor
                active_cases += 1
                unknown_exposure[curr] += case.amount_at_risk.amount_minor
            if case.workflow_state.value == "WAITING_APPROVAL":
                awaiting_approval += 1
            if case.workflow_state.value in ("EXECUTING", "PENDING_EXECUTION"):
                in_execution_count += 1"""
content = content.replace(old_analytics_loop, new_analytics_loop)

old_analytics_ret = """        return {
            "performance_7d": performance_7d,
            "revenue_at_risk": revenue_at_risk,
            "verified_recovered": verified_recovered,
            "active_cases": active_cases,
            "outcomeDistribution": outcome_distribution,
            "funnel": funnel,
        }"""
new_analytics_ret = """        return {
            "performance_7d": performance_7d,
            "revenue_at_risk": revenue_at_risk,
            "verified_recovered": verified_recovered,
            "active_cases": active_cases,
            "awaiting_approval": awaiting_approval,
            "in_execution": in_execution_count,
            "outcomeDistribution": outcome_distribution,
            "funnel": funnel,
        }"""
content = content.replace(old_analytics_ret, new_analytics_ret)

with open('recoverai/api/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated main.py analytics")
