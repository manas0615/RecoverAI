import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from recoverai.api.main import container


def clean_db():
    print("Connecting to database via container...")
    with container.tm.transaction() as conn:
        print("Cleaning existing operational data...")
        conn.execute("DELETE FROM verification_records")
        conn.execute("DELETE FROM recovery_actions")
        conn.execute("DELETE FROM policy_decisions")
        conn.execute("DELETE FROM intervention_plan_candidates")
        conn.execute("DELETE FROM intervention_plans")
        conn.execute("DELETE FROM intervention_candidates")
        conn.execute("DELETE FROM cause_assessments")
        conn.execute("DELETE FROM risk_assessments")
        conn.execute("DELETE FROM case_source_events")
        conn.execute("DELETE FROM recovery_cases")
        conn.execute("DELETE FROM revenue_events")
        conn.execute("DELETE FROM audit_events")

    print("Database is now clean and ready for REAL Razorpay Test Mode events.")


if __name__ == "__main__":
    clean_db()
