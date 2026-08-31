import re

with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace get_case implementation
pattern = re.compile(r'@app\.get\("/recovery-cases/\{case_id\}", dependencies=\[Depends\(require_frontend_key\)\]\)\ndef get_case\(case_id: str\):.*?return result', re.DOTALL)

new_get_case = """@app.get("/recovery-cases/{case_id}", dependencies=[Depends(require_frontend_key)])
def get_case(case_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository
        from recoverai.persistence.repositories.audit import AuditRepository
        
        repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)
        audit_repo = AuditRepository(conn)
        
        try:
            case = repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        events = [event_repo.get(eid) for eid in case.source_event_ids]

        result = case_to_dict(case)
        result["events"] = [
            {
                "event_id": e.event_id.value,
                "event_type": e.event_type.value,
                "amount_minor": e.amount.amount_minor if e.amount else None,
                "currency": e.amount.currency.value if e.amount else None,
                "occurred_at": e.occurred_at.isoformat(),
                "external_reference": e.external_reference,
                "metadata": e.metadata,
            }
            for e in events
            if e
        ]
        
        # Gather evidence
        result["failure_code"] = "UNKNOWN"
        result["historical_failure_count"] = len([e for e in events if e and "FAIL" in e.event_type.value])
        for e in events:
            if e and e.metadata.get("error_code"):
                result["failure_code"] = e.metadata["error_code"]
                break
            if e and e.metadata.get("failure_reason"):
                result["failure_code"] = e.metadata["failure_reason"]
                break
                
        # Gather Recommendation
        result["recommendation"] = "N/A"
        result["confidence"] = None
        result["reasoning"] = None
        result["provenance"] = None
        
        audit_events = audit_repo.get_by_case(case_id)
        for ae in audit_events:
            if ae.event_type.value == "LLM_RECOMMENDATION_CREATED" and ae.metadata:
                if "action" in ae.metadata:
                    result["recommendation"] = ae.metadata["action"]
                if "confidence" in ae.metadata:
                    result["confidence"] = ae.metadata["confidence"]
                if "reasoning" in ae.metadata:
                    result["reasoning"] = ae.metadata["reasoning"]
                
                # Provenance
                actor_id = ae.actor.id if ae.actor else "UNKNOWN"
                if "gemini" in actor_id.lower() or "gemini" in str(ae.metadata).lower():
                    result["provenance"] = "Gemini"
                else:
                    result["provenance"] = "Deterministic Fallback"
                    
            if ae.event_type.value == "POLICY_DECISION_RECORDED" and ae.metadata:
                result["policy_decision"] = ae.metadata.get("decision")
                result["policy_reasons"] = ae.metadata.get("reasons", [])
                
        # Find action_id for approval
        try:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            action_repo = RecoveryActionRepository(conn)
            cur = conn.execute("SELECT action_id FROM recovery_actions WHERE case_id = ? ORDER BY requested_at DESC LIMIT 1", (case_id,))
            row = cur.fetchone()
            if row:
                result["action_id"] = row["action_id"]
        except Exception:
            pass

        return result"""

if pattern.search(content):
    content = pattern.sub(new_get_case.strip(), content)
    with open('recoverai/api/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched get_case successfully")
else:
    print("Could not find get_case to patch")
