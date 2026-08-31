import re

with open('recoverai/persistence/repositories/verification.py', 'r') as f:
    content = f.read()

new_methods = '''
    def get_by_case(self, case_id: RecoveryCaseId) -> list[VerificationRecord]:
        rows = self.conn.execute(
            "SELECT * FROM verification_records WHERE case_id = ? ORDER BY checked_at DESC",
            (case_id.value,),
        ).fetchall()
        
        records = []
        for row in rows:
            evidence_ref = None
            if row["evidence_reference_json"]:
                data = json.loads(row["evidence_reference_json"])
                evidence_ref = EvidenceReference(
                    source_type=EvidenceSourceType(data["source_type"]),
                    source_id=data["source_id"],
                    observed_at=datetime.fromisoformat(data["observed_at"]),
                    field=data.get("field"),
                )
            records.append(VerificationRecord(
                verification_id=VerificationRecordId(row["verification_id"]),
                action_id=RecoveryActionId(row["action_id"]),
                case_id=RecoveryCaseId(row["case_id"]),
                verification_source=VerificationSource(row["verification_source"]),
                verified_state=VerifiedState(row["verified_state"]),
                external_reference=row["external_reference"],
                evidence_reference=evidence_ref,
                checked_at=datetime.fromisoformat(row["checked_at"]),
            ))
        return records
'''

if "def get_by_case" not in content:
    content += new_methods
    with open('recoverai/persistence/repositories/verification.py', 'w') as f:
        f.write(content)
