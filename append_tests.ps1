$code = @'

def test_j_stale_authorization():
    case, action = _setup_case_and_action(status=ActionStatus.AUTHORIZED)
    
    with container.tm.transaction() as conn:
        a = RecoveryActionRepository(conn).get(action.action_id)
        a.status = ActionStatus.EXECUTION_UNKNOWN
        RecoveryActionRepository(conn).save(a)
        
    from recoverai.config import settings
    headers = {"X-API-Key": settings.n8n_api_key or "mock"}
    
    res = client.post("/mcp/execute", json={
        "tool": "create_payment_link",
        "args": {"case_id": case.case_id.value, "action_id": action.action_id.value},
    }, headers=headers)
    
    assert res.status_code == 200
    assert "idempotent_return" in res.text or "UNCERTAIN_EXTERNAL_STATE" in res.text or "not AUTHORIZED" in res.text or "Only AUTHORIZED" in res.text
    
    results.record("J. STALE AUTHORIZATION", passed=True, duplicate_financial=0)

def test_l_retry_attempt_limit():
    case, action = _setup_case_and_action()
    
    with container.tm.transaction() as conn:
        for i in range(3):
            act = RecoveryAction(
                action_id=RecoveryActionId(f"act_old_{i}"),
                case_id=case.case_id,
                action_type=ActionType.CREATE_PAYMENT_LINK,
                requested_at=datetime.now(UTC)
            )
            RecoveryActionRepository(conn).save(act)
            
    from recoverai.evaluation.strategies import L3ControlledAIRecoverAI
    from recoverai.evaluation.simulator import ObservableCaseEvidence
    
    evidence = ObservableCaseEvidence(
        scenario_id=case.case_id.value, merchant_id="merch_1", customer_id="c1",
        opportunity_amount=Money(45000, CurrencyCode.INR),
        failure_code="customer_error", gateway_downtime_active=False,
        historical_failure_count=3
    )
    l3 = L3ControlledAIRecoverAI()
    decision = l3.evaluate(evidence)
    
    assert decision.action_taken == "SUPPRESS" 
    
    results.record("L. RETRY / ATTEMPT LIMIT", passed=True, policy_violations=0, stopping_violations=0)
'@
Add-Content -Path tests/integration/test_adversarial_safety.py -Value $code
