import os
import sys

if "--development-demo-reset-confirm" not in sys.argv:
    print("ERROR: This is a destructive operation.")
    print("You must pass --development-demo-reset-confirm to execute this script.")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

if os.environ.get("ENVIRONMENT", "").lower() == "production":
    print("ERROR: Cannot run demo reset in production environment.")
    sys.exit(1)

from recoverai.persistence.connection import TransactionManager

def reset_db():
    print("Starting clean demo reset...")
    tm = TransactionManager()
    
    tables_to_clear = [
        "audit_events",
        "verification_records",
        "recovery_actions",
        "policy_decisions",
        "intervention_candidates",
        "intervention_plan_candidates",
        "intervention_plans",
        "cause_assessments",
        "risk_assessments",
        "case_source_events",
        "revenue_events",
        "recovery_cases",
    ]
    
    with tm.transaction() as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        for table in tables_to_clear:
            conn.execute(f"DELETE FROM {table};")
            print(f"Cleared table: {table}")
        conn.execute("PRAGMA foreign_keys = ON;")
            
    print("Database reset successful.")

if __name__ == "__main__":
    reset_db()
