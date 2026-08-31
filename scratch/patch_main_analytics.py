import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

# We need to replace get_analytics entirely
match = re.search(r'(@app\.get\("/analytics", dependencies=\[Depends\(require_frontend_key\)\]\)\ndef get_analytics\(\):.*?)(?=@app\.post\("/recovery-cases/\{case_id\}/abort")', content, flags=re.DOTALL)

if not match:
    print("Could not find get_analytics block")
    exit(1)

old_block = match.group(1)

new_block = """@app.get("/analytics", dependencies=[Depends(require_frontend_key)])
def get_analytics():
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.verification import VerificationRecordRepository
        
        repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        verif_repo = VerificationRecordRepository(conn)
        
        cur = conn.execute("SELECT case_id FROM recovery_cases")
        cases = []
        for row in cur.fetchall():
            c = repo.get(RecoveryCaseId(row["case_id"]))
            if c:
                cases.append(c)

        revenue_at_risk = {"INR": 0}
        verified_recovered = {"INR": 0}
        
        outcome_distribution = {
            "RECOVERED": 0,
            "EXECUTING": 0,
            "AWAITING_APPROVAL": 0,
            "ESCALATED": 0,
            "UNRECOVERABLE": 0,
            "VERIF_PENDING": 0,
        }
        
        funnel = {
            "DETECTED": len(cases),
            "ANALYZED": 0,
            "RECOMMENDED": 0,
            "HUMAN_APPROVAL": 0,
            "EXECUTING": 0,
            "RESPONDED": 0,
            "VERIFYING": 0,
            "VERIFIED": 0,
        }

        # Provenance
        recommendation_source = {
            "Gemini": 0,
            "Deterministic Fallback": 0
        }
        
        # Failure Causes
        failure_causes = {}
        
        # Verification Outcomes
        verification_outcomes = {
            "Provider Matched": 0,
            "Mismatch Detected": 0,
            "Verification Pending": 0
        }

        # Intervention Strategies
        intervention_perf = {}

        total_eligible = 0
        total_verified_cases = 0
        
        total_verifications = 0
        total_verifications_matched = 0

        from datetime import datetime, UTC, timedelta
        now = datetime.now(UTC)
        performance_7d = []
        for i in range(6, -1, -1):
            target_date = (now - timedelta(days=i)).date()
            performance_7d.append({
                "date": target_date.isoformat(),
                "recovered": 0,
                "at_risk": 0
            })

        for case in cases:
            curr = case.amount_at_risk.currency.value
            if curr not in revenue_at_risk:
                revenue_at_risk[curr] = 0
            if curr not in verified_recovered:
                verified_recovered[curr] = 0

            if case.status.value == "OPEN":
                revenue_at_risk[curr] += case.amount_at_risk.amount_minor
                
            # Recovery Outcomes logic
            st = case.workflow_state.value
            out_type = case.outcome_type.value if case.outcome_type else None
            
            if out_type == "RECOVERED":
                outcome_distribution["RECOVERED"] += 1
                verified_recovered[curr] += (case.recovered_amount.amount_minor if case.recovered_amount else case.amount_at_risk.amount_minor)
                total_verified_cases += 1
            elif out_type in ("FAILED_PERMANENTLY", "DENIED"):
                outcome_distribution["UNRECOVERABLE"] += 1
            elif out_type == "ESCALATED" or st == "ESCALATED":
                outcome_distribution["ESCALATED"] += 1
            elif st == "WAITING_APPROVAL":
                outcome_distribution["AWAITING_APPROVAL"] += 1
            elif st in ("EXECUTING", "PENDING_EXECUTION"):
                outcome_distribution["EXECUTING"] += 1
            elif st in ("VERIFYING", "VERIFICATION_PENDING", "VERIFICATION_STARTED"):
                outcome_distribution["VERIF_PENDING"] += 1
                
            # Funnel Logic
            if st in ("ANALYZING", "POLICY_REVIEW", "WAITING_APPROVAL", "PENDING_EXECUTION", "EXECUTING", "VERIFYING", "CLOSED", "ESCALATED"):
                funnel["ANALYZED"] += 1
                if case.provenance:
                    funnel["RECOMMENDED"] += 1
                    
            if st in ("WAITING_APPROVAL", "PENDING_EXECUTION", "EXECUTING", "VERIFYING", "CLOSED", "ESCALATED") and (case.rules_matched and any(r.action == "REQUIRE_APPROVAL" for r in case.rules_matched)):
                funnel["HUMAN_APPROVAL"] += 1
                
            if st in ("PENDING_EXECUTION", "EXECUTING", "VERIFYING", "CLOSED") and out_type not in ("DENIED", "ESCALATED"):
                funnel["EXECUTING"] += 1
                if st in ("VERIFYING", "CLOSED"):
                    funnel["RESPONDED"] += 1
                if st in ("VERIFYING", "CLOSED") and out_type != "FAILED_PERMANENTLY":
                    funnel["VERIFYING"] += 1
                    
            if out_type == "RECOVERED":
                funnel["VERIFIED"] += 1
                
            # Provenance
            if case.provenance == "Gemini":
                recommendation_source["Gemini"] += 1
            elif case.provenance == "Deterministic Fallback":
                recommendation_source["Deterministic Fallback"] += 1
                
            # Actions for intervention
            actions = action_repo.get_by_case(case.id.value)
            for action in actions:
                s_type = action.strategy_type.value if hasattr(action.strategy_type, 'value') else str(action.strategy_type)
                if s_type not in intervention_perf:
                    intervention_perf[s_type] = {"cases": 0, "recovered": 0, "failed": 0, "pending": 0}
                intervention_perf[s_type]["cases"] += 1
                
                ast = action.status.value if hasattr(action.status, 'value') else str(action.status)
                if ast == "FAILED":
                    intervention_perf[s_type]["failed"] += 1
                    # Failure cause
                    cause = action.failure_reason or "Unknown Error"
                    failure_causes[cause] = failure_causes.get(cause, 0) + 1
                elif ast == "COMPLETED" and out_type == "RECOVERED":
                    intervention_perf[s_type]["recovered"] += 1
                else:
                    intervention_perf[s_type]["pending"] += 1
                    
            # Verification logic
            verifs = verif_repo.get_by_case(case.id.value)
            if verifs:
                total_verifications += 1
                v_st = verifs[0].verified_state.value if hasattr(verifs[0].verified_state, 'value') else str(verifs[0].verified_state)
                if v_st == "SUCCESS":
                    verification_outcomes["Provider Matched"] += 1
                    total_verifications_matched += 1
                elif v_st == "FAILURE":
                    verification_outcomes["Mismatch Detected"] += 1
                else:
                    verification_outcomes["Verification Pending"] += 1
            elif st in ("VERIFYING", "VERIFICATION_PENDING"):
                verification_outcomes["Verification Pending"] += 1

            if case.status.value != "OPEN" and out_type not in ("UNKNOWN_OR_MANUAL", "ESCALATED"):
                total_eligible += 1

            # Performance Chart
            if case.status.value == "OPEN":
                case_date = case.opened_at.date()
                for day in performance_7d:
                    if day["date"] == case_date.isoformat():
                        day["at_risk"] += case.amount_at_risk.amount_minor
                        
            if out_type == "RECOVERED":
                recovery_dt = case.closed_at or case.updated_at or case.opened_at
                recovery_date = recovery_dt.date()
                for day in performance_7d:
                    if day["date"] == recovery_date.isoformat():
                        day["recovered"] += case.recovered_amount.amount_minor if case.recovered_amount else case.amount_at_risk.amount_minor

        rec_rate = (total_verified_cases / total_eligible * 100) if total_eligible > 0 else 0
        verif_rate = (total_verifications_matched / total_verifications * 100) if total_verifications > 0 else 0

        int_perf_list = []
        for s_type, perf in intervention_perf.items():
            r_rate = (perf["recovered"] / perf["cases"] * 100) if perf["cases"] > 0 else 0
            int_perf_list.append({
                "strategy": s_type,
                "cases": perf["cases"],
                "recovered": perf["recovered"],
                "failed": perf["failed"],
                "pending": perf["pending"],
                "recovery_rate": round(r_rate, 1)
            })

        return {
            "recovery_rate": round(rec_rate, 1),
            "verification_rate": round(verif_rate, 1),
            "revenue_at_risk": revenue_at_risk,
            "verified_recovered": verified_recovered,
            "performance_7d": performance_7d,
            "recovery_outcomes": outcome_distribution,
            "intervention_performance": int_perf_list,
            "recommendation_source": recommendation_source,
            "lifecycle": [{"stage": k, "count": v} for k, v in funnel.items()],
            "failure_causes": [{"cause": k, "count": v} for k, v in failure_causes.items()],
            "verification_outcomes": verification_outcomes
        }

"""

content = content.replace(old_block, new_block)

with open('recoverai/api/main.py', 'w') as f:
    f.write(content)
print("Patched main.py")
