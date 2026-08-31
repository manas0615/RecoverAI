import re

with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_list_cases = """
@app.get("/recovery-cases", dependencies=[Depends(require_frontend_key)])
def list_cases():
    with container.tm.transaction() as conn:
        cur = conn.execute("SELECT case_id FROM recovery_cases ORDER BY opened_at DESC")
        repo = RecoveryCaseRepository(conn)
        
        # We need failure codes and recommendations
        cases = []
        for row in cur.fetchall():
            case_id_val = row["case_id"]
            c = repo.get(RecoveryCaseId(case_id_val))
            if c:
                d = case_to_dict(c)
                
                # Fetch failure code from events
                d["failure_code"] = "UNKNOWN"
                from recoverai.persistence.repositories.event import RevenueEventRepository
                event_repo = RevenueEventRepository(conn)
                
                events = [event_repo.get(eid) for eid in c.source_event_ids]
                for e in events:
                    if e and e.metadata.get("error_code"):
                        d["failure_code"] = e.metadata["error_code"]
                        break
                    if e and e.metadata.get("failure_reason"):
                        d["failure_code"] = e.metadata["failure_reason"]
                        break
                        
                # Fetch recommendation from audit log
                d["recommendation"] = "N/A"
                from recoverai.persistence.repositories.audit import AuditRepository
                audit_repo = AuditRepository(conn)
                audit_events = audit_repo.get_by_case(case_id_val)
                for ae in audit_events:
                    if ae.event_type.value == "LLM_RECOMMENDATION_CREATED" and ae.metadata and "action" in ae.metadata:
                        d["recommendation"] = ae.metadata["action"]

                # Determine updated_at
                updated_at = c.updated_at or c.opened_at
                d["updated_at"] = updated_at.isoformat()
                
                cases.append(d)
                
        return {"cases": cases}
"""

pattern = re.compile(r'@app\.get\("/recovery-cases", dependencies=\[Depends\(require_frontend_key\)\]\)\ndef list_cases\(\):.*?return \{"cases": cases\}', re.DOTALL)
if pattern.search(content):
    content = pattern.sub(new_list_cases.strip(), content)
    with open('recoverai/api/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched list_cases successfully")
else:
    print("Could not find list_cases to patch")
