import json
import sqlite3
from datetime import datetime

from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType
from recoverai.domain.identifiers import (
    RecoveryActionId,
    RecoveryCaseId,
    VerificationRecordId,
)
from recoverai.domain.verification import (
    VerificationRecord,
    VerificationSource,
    VerifiedState,
)


class VerificationRecordRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, record: VerificationRecord) -> None:
        evidence_json = None
        if record.evidence_reference:
            evidence_json = json.dumps(
                {
                    "source_type": record.evidence_reference.source_type.value,
                    "source_id": record.evidence_reference.source_id,
                    "observed_at": record.evidence_reference.observed_at.isoformat(),
                    "field": record.evidence_reference.field,
                }
            )

        self.conn.execute(
            """
            INSERT INTO verification_records (
                verification_id, action_id, case_id, verification_source,
                verified_state, external_reference, evidence_reference_json, checked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.verification_id.value,
                record.action_id.value,
                record.case_id.value,
                record.verification_source.value,
                record.verified_state.value,
                record.external_reference,
                evidence_json,
                record.checked_at.isoformat(),
            ),
        )

    def get(self, verification_id: VerificationRecordId) -> VerificationRecord | None:
        row = self.conn.execute(
            "SELECT * FROM verification_records WHERE verification_id = ?",
            (verification_id.value,),
        ).fetchone()

        if not row:
            return None

        evidence_ref = None
        if row["evidence_reference_json"]:
            data = json.loads(row["evidence_reference_json"])
            evidence_ref = EvidenceReference(
                source_type=EvidenceSourceType(data["source_type"]),
                source_id=data["source_id"],
                observed_at=datetime.fromisoformat(data["observed_at"]),
                field=data.get("field"),
            )

        return VerificationRecord(
            verification_id=VerificationRecordId(row["verification_id"]),
            action_id=RecoveryActionId(row["action_id"]),
            case_id=RecoveryCaseId(row["case_id"]),
            verification_source=VerificationSource(row["verification_source"]),
            verified_state=VerifiedState(row["verified_state"]),
            external_reference=row["external_reference"],
            evidence_reference=evidence_ref,
            checked_at=datetime.fromisoformat(row["checked_at"]),
        )

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
