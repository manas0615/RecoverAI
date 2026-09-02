$code = @'

def test_t_execution_success_without_verification():
    case, action = _setup_case_and_action(status=ActionStatus.AUTHORIZED)
    
    from recoverai.config import settings
    headers = {"X-API-Key": settings.n8n_api_key or "mock"}
    
    with mock.patch("recoverai.integrations.razorpay.adapter.RazorpayAdapter.execute_payment_link") as mock_exec:
        from recoverai.integrations.razorpay.adapter import RazorpayExecutionResult, RazorpayExecutionResultType
        mock_exec.return_value = RazorpayExecutionResult(
            result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
            provider_reference="plink_succ",
            short_url="https://rzp.io/i/succ"
        )
        
        res = client.post("/mcp/execute", json={
            "tool": "create_payment_link",
            "args": {"case_id": case.case_id.value, "action_id": action.action_id.value},
        }, headers=headers)
        
        assert res.status_code == 200
        
        with container.tm.transaction() as conn:
            c = RecoveryCaseRepository(conn).get(case.case_id)
            a = RecoveryActionRepository(conn).get(action.action_id)
            assert a.status == ActionStatus.VERIFICATION_PENDING
            assert c.status == RecoveryCaseStatus.OPEN
            
    results.record("T. EXECUTION SUCCESS WITHOUT VALID VERIFICATION", passed=True, false_recovery=0)

'@
Add-Content -Path tests/integration/test_adversarial_safety.py -Value $code
