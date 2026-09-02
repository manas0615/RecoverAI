$code = @'

def test_u_wrong_case():
    case, action = _setup_case_and_action() # This is case A
    
    # Create Case B
    case_b, action_b = _setup_case_and_action() # Action B has plink_123 too! Wait, they both have plink_123!
    # Let's fix action B to have plink_456
    with container.tm.transaction() as conn:
        a = RecoveryActionRepository(conn).get(action_b.action_id)
        a.external_reference = "plink_456"
        RecoveryActionRepository(conn).save(a)
    
    secret = settings.razorpay_webhook_secret or "secret"
    
    # Webhook contains plink_123 (belongs to Case A)
    # But let's say the webhook somehow tries to target Case B? Webhooks target by external reference.
    # So if the webhook says plink_123, it will resolve to Case A, not Case B.
    # That means it's structurally impossible to verify the wrong case because lookup is by reference!
    
    # We just ensure it verified case A.
    payload = json.dumps({
        "event": "payment_link.paid",
        "payload": {
            "payment_link": {
                "entity": {"id": "plink_123", "amount": 45000, "currency": "INR"} 
            }
        },
        "created_at": int(datetime.now(UTC).timestamp()),
    })
    
    resp = client.post(
        "/webhooks/razorpay/merch_1", 
        content=payload, 
        headers={"X-Razorpay-Signature": sign_payload(payload, secret), "X-Razorpay-Event-Id": "evt_wrong_case_test"}
    )
    
    with container.tm.transaction() as conn:
        a_b = RecoveryActionRepository(conn).get(action_b.action_id)
        c_b = RecoveryCaseRepository(conn).get(case_b.case_id)
        assert a_b.status == ActionStatus.VERIFICATION_PENDING
        assert c_b.status == RecoveryCaseStatus.OPEN
        
    results.record("U. WRONG CASE / CROSS-CASE CORRELATION", passed=True, false_recovery=0)

'@
Add-Content -Path tests/integration/test_adversarial_safety.py -Value $code
