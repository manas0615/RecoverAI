import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

# For list_cases: We just need to know if there's a verification record, 
# but actually `action_status` already tells us if it's VERIFIED_SUCCESS, VERIFIED_FAILURE, or VERIFICATION_PENDING.
# The KPI numbers in UI can just use `action_status`.
# The only thing we might want to add is `verification_state` just in case, but `action_status` is enough for the queue.

# For get_case:
old_get_case_end = """        # Find action details for execution UI
        try:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            action_repo = RecoveryActionRepository(conn)
            actions = action_repo.get_by_case(case_id)
            if actions:
                latest_action = sorted(actions, key=lambda x: x.requested_at, reverse=True)[0]
                result["action_type"] = latest_action.action_type.value
                result["action_status"] = latest_action.status.value
                result["action_id"] = latest_action.action_id.value
                result["provider"] = latest_action.provider
                result["external_reference"] = latest_action.external_reference
                result["action_requested_at"] = latest_action.requested_at.isoformat() if latest_action.requested_at else None
                result["action_executed_at"] = latest_action.executed_at.isoformat() if latest_action.executed_at else None
        except Exception:
            pass

        return result"""

new_get_case_end = """        # Find action details and verification details for execution & verification UI
        try:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            from recoverai.persistence.repositories.verification import VerificationRecordRepository
            from recoverai.domain.identifiers import RecoveryCaseId
            action_repo = RecoveryActionRepository(conn)
            ver_repo = VerificationRecordRepository(conn)
            
            actions = action_repo.get_by_case(case_id)
            if actions:
                latest_action = sorted(actions, key=lambda x: x.requested_at, reverse=True)[0]
                result["action_type"] = latest_action.action_type.value
                result["action_status"] = latest_action.status.value
                result["action_id"] = latest_action.action_id.value
                result["provider"] = latest_action.provider
                result["external_reference"] = latest_action.external_reference
                result["action_requested_at"] = latest_action.requested_at.isoformat() if latest_action.requested_at else None
                result["action_executed_at"] = latest_action.executed_at.isoformat() if latest_action.executed_at else None
                
                # Verification Details
                records = ver_repo.get_by_case(RecoveryCaseId(case_id))
                if records:
                    latest_record = records[0]
                    result["verification_state"] = latest_record.verified_state.value
                    result["verification_source"] = latest_record.verification_source.value
                    result["verification_checked_at"] = latest_record.checked_at.isoformat()
                    
                    # Gather observed evidence details if available
                    if latest_action.external_reference:
                        events = event_repo.get_by_external_reference(latest_action.external_reference)
                        for ev in events:
                            if ev.event_type.value == "PAYMENT_LINK_PAID":
                                result["observed_event_type"] = ev.event_type.value
                                result["observed_amount_minor"] = ev.amount.amount_minor if ev.amount else None
                                result["observed_currency"] = ev.amount.currency.value if ev.amount else None
                                result["observed_reference"] = ev.external_reference
                                break
                    elif latest_action.idempotency_key:
                        events = event_repo.get_by_merchant_and_type(case.merchant_id, "PAYMENT_LINK_PAID")
                        for ev in events:
                            # Mock extract ref
                            result["observed_event_type"] = ev.event_type.value
                            result["observed_amount_minor"] = ev.amount.amount_minor if ev.amount else None
                            result["observed_currency"] = ev.amount.currency.value if ev.amount else None
                            result["observed_reference"] = ev.external_reference
                            break
                            
        except Exception:
            pass

        return result"""

if 'result["verification_state"]' not in content:
    content = content.replace(old_get_case_end, new_get_case_end)
    with open('recoverai/api/main.py', 'w') as f:
        f.write(content)
