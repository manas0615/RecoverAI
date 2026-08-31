with open("tests/unit/api/test_api.py", "a") as f:
    f.write('''

def clear_db():
    from recoverai.api.main import container
    with container.tm.transaction() as conn:
        conn.execute("DELETE FROM recovery_cases")
        conn.execute("DELETE FROM recovery_actions")
        conn.execute("DELETE FROM verification_records")
        conn.execute("DELETE FROM audit_events")
        conn.execute("DELETE FROM revenue_events")

def test_populated_data_contracts():
    clear_db()
    
    from recoverai.api.main import container
    from recoverai.domain.identifiers import RecoveryCaseId, MerchantId, RevenueEventId
    from recoverai.domain.case import RecoveryCase, RecoveryWorkflowState, RecoveryOutcomeType, RecoveryStatus
    from recoverai.domain.money import RevenueAmount, Money
    from recoverai.domain.action import RecoveryAction, RecoveryActionId, ActionType, ActionStatus, PolicyDecisionId
    from recoverai.domain.audit import AuditEvent, AuditEventType, AuditActor, AuditActorType
    from datetime import datetime, UTC
    
    now = datetime.now(UTC)
    
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_populated"),
        merchant_id=MerchantId("merch_1"),
        revenue_source="PAYMENT_LINK",
        amount_at_risk=RevenueAmount(Money(10000, "INR")),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")}
    )
    
    action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
        policy_decision_id=PolicyDecisionId("dec_1"),
        status=ActionStatus.PROPOSED
    )
    
    audit_event = AuditEvent(
        event_type=AuditEventType.LLM_RECOMMENDATION_CREATED,
        actor=AuditActor(type=AuditActorType.LLM_AGENT, id="gemini-1.5"),
        case_id=case.case_id,
        timestamp=now,
        metadata={"recommended_action": "CREATE_PAYMENT_LINK", "confidence": 0.95}
    )
    
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.audit import AuditRepository
        
        RecoveryCaseRepository(conn).save(case)
        RecoveryActionRepository(conn).save(action)
        AuditRepository(conn).append(audit_event)
        
    # Test case detail populated
    response = client.get(f"/recovery-cases/{case.case_id.value}", headers=FRONTEND_HEADERS)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation"] == "CREATE_PAYMENT_LINK"
    assert data["provenance"] == "Gemini"
    assert data["action_id"] == "act_1"
    
    # Test analytics populated
    response = client.get("/analytics", headers=FRONTEND_HEADERS)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation_source"]["Gemini"] == 1
    
    clear_db()
''')
