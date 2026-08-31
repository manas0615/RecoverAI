import re

# 1. Update recoverai/api/main.py for temporal correctness
with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    api_content = f.read()

old_loop = '''        for case in cases:
            case_date = case.opened_at.date()
            for day in performance_7d:
                if day["date"] == case_date.isoformat():
                    if case.status.value == "OPEN":
                        day["at_risk"] += case.amount_at_risk.amount_minor
                    if case.outcome_type and case.outcome_type.value == "RECOVERED":
                        day["recovered"] += case.recovered_amount.amount_minor if case.recovered_amount else case.amount_at_risk.amount_minor'''

new_loop = '''        for case in cases:
            # Revenue at Risk uses the opened_at date (when the revenue was put at risk)
            if case.status.value == "OPEN":
                case_date = case.opened_at.date()
                for day in performance_7d:
                    if day["date"] == case_date.isoformat():
                        day["at_risk"] += case.amount_at_risk.amount_minor
                        
            # Verified Recovered uses the closed_at or updated_at date (when the recovery was verified)
            if case.outcome_type and case.outcome_type.value == "RECOVERED":
                recovery_dt = case.closed_at or case.updated_at or case.opened_at
                recovery_date = recovery_dt.date()
                for day in performance_7d:
                    if day["date"] == recovery_date.isoformat():
                        day["recovered"] += case.recovered_amount.amount_minor if case.recovered_amount else case.amount_at_risk.amount_minor'''

if old_loop in api_content:
    api_content = api_content.replace(old_loop, new_loop)
    with open('recoverai/api/main.py', 'w', encoding='utf-8') as f:
        f.write(api_content)
else:
    print("WARNING: Could not find API loop to patch")


# 2. Update frontend/src/pages/Dashboard.tsx for semantic interaction
with open('frontend/src/pages/Dashboard.tsx', 'r', encoding='utf-8') as f:
    dash_content = f.read()

# Replace the Link wrapper with a div
dash_content = dash_content.replace(
    '<Link to={`/cases/${pd?.id}`} className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm hover:border-[var(--color-primary)] hover:bg-[var(--color-surface-secondary)] transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">',
    '<div className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">'
)
# The end tag for that wrapper is at the end of the priority card. I replaced it previously with:
dash_content = dash_content.replace(
    '          )}\n        </Link>',
    '          )}\n        </div>'
)

# Update the Review Case button to a Link
old_review_btn = '<button className="px-4 py-2 rounded text-sm font-medium border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">\n                      Review Case\n                    </button>'
new_review_link = '<Link to={`/cases/${pd?.id}`} className="px-4 py-2 rounded text-sm font-medium border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">\n                      Review Case &rarr;\n                    </Link>'
if old_review_btn in dash_content:
    dash_content = dash_content.replace(old_review_btn, new_review_link)
else:
    print("WARNING: Could not find Review Case button")

# Remove stopPropagation from handleApprove button
old_approve = 'onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleApprove(); }}'
new_approve = 'onClick={handleApprove}'
dash_content = dash_content.replace(old_approve, new_approve)

with open('frontend/src/pages/Dashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(dash_content)

print("Patched Dashboard")
