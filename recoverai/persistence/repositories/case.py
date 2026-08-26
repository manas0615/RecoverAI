import sqlite3

from recoverai.domain import (
    CustomerId,
    MerchantId,
    RecoveryCase,
    RecoveryCaseId,
    RecoveryCaseStatus,
    RecoveryOutcomeValue,
    RevenueEventId,
    RevenueSource,
)
from recoverai.persistence.exceptions import DuplicateEntityError
from recoverai.persistence.mappers import dt_to_str, row_to_revenue_amount, str_to_dt


class RecoveryCaseRepository:
    """
    Repository for RecoveryCase. Handles the case itself and its event linkage.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, case: RecoveryCase) -> None:
        """
        Upserts the RecoveryCase and completely synchronizes its linked source_event_ids.
        This must be called within a transaction!
        """
        # Determine if insert or update
        cur = self.conn.execute(
            "SELECT 1 FROM recovery_cases WHERE case_id = ?", (case.case_id.value,)
        )
        exists = cur.fetchone() is not None

        rec_amt_minor = (
            case.recovered_amount.amount_minor if case.recovered_amount else None
        )
        rec_currency = (
            case.recovered_amount.currency.value if case.recovered_amount else None
        )

        try:
            if exists:
                # Update (could use optimistic concurrency if we tracked a version, but here we just update)
                self.conn.execute(
                    """
                    UPDATE recovery_cases SET
                        customer_id = ?,
                        status = ?,
                        outcome_type = ?,
                        recovered_amount_minor = ?,
                        recovered_amount_currency = ?,
                        updated_at = ?,
                        closed_at = ?
                    WHERE case_id = ?
                """,
                    (
                        case.customer_id.value if case.customer_id else None,
                        case.status.value,
                        case.outcome_type.value if case.outcome_type else None,
                        rec_amt_minor,
                        rec_currency,
                        dt_to_str(case.updated_at),
                        dt_to_str(case.closed_at),
                        case.case_id.value,
                    ),
                )
            else:
                # Insert
                self.conn.execute(
                    """
                    INSERT INTO recovery_cases (
                        case_id, merchant_id, customer_id, revenue_source,
                        amount_at_risk_minor, amount_at_risk_currency,
                        status, outcome_type, recovered_amount_minor, recovered_amount_currency,
                        opened_at, updated_at, closed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        case.case_id.value,
                        case.merchant_id.value,
                        case.customer_id.value if case.customer_id else None,
                        case.revenue_source.value,
                        case.amount_at_risk.amount_minor,
                        case.amount_at_risk.currency.value,
                        case.status.value,
                        case.outcome_type.value if case.outcome_type else None,
                        rec_amt_minor,
                        rec_currency,
                        dt_to_str(case.opened_at),
                        dt_to_str(case.updated_at),
                        dt_to_str(case.closed_at),
                    ),
                )

            # Sync source_event_ids (replace all or just insert missing)
            # Simplest safe way in a transaction: DELETE and INSERT
            self.conn.execute(
                "DELETE FROM case_source_events WHERE case_id = ?",
                (case.case_id.value,),
            )
            for eid in case.source_event_ids:
                self.conn.execute(
                    "INSERT INTO case_source_events (case_id, event_id) VALUES (?, ?)",
                    (case.case_id.value, eid.value),
                )

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateEntityError(f"Duplicate entity: {e}")
            raise

    def get(self, case_id: RecoveryCaseId) -> RecoveryCase | None:
        cur = self.conn.execute(
            "SELECT * FROM recovery_cases WHERE case_id = ?", (case_id.value,)
        )
        row = cur.fetchone()
        if not row:
            return None

        events_cur = self.conn.execute(
            "SELECT event_id FROM case_source_events WHERE case_id = ?",
            (case_id.value,),
        )
        event_ids = {RevenueEventId(erow["event_id"]) for erow in events_cur.fetchall()}

        return self._map_row(row, event_ids)

    def _map_row(self, row: dict, event_ids: set[RevenueEventId]) -> RecoveryCase:
        return RecoveryCase(
            case_id=RecoveryCaseId(row["case_id"]),
            merchant_id=MerchantId(row["merchant_id"]),
            customer_id=CustomerId(row["customer_id"]) if row["customer_id"] else None,
            revenue_source=RevenueSource(row["revenue_source"]),
            amount_at_risk=row_to_revenue_amount(
                row["amount_at_risk_minor"], row["amount_at_risk_currency"]
            ),  # type: ignore
            opened_at=str_to_dt(row["opened_at"]),  # type: ignore
            source_event_ids=event_ids,
            status=RecoveryCaseStatus(row["status"]),
            outcome_type=RecoveryOutcomeValue(row["outcome_type"])
            if row["outcome_type"]
            else None,
            recovered_amount=row_to_revenue_amount(
                row["recovered_amount_minor"], row["recovered_amount_currency"]
            ),
            updated_at=str_to_dt(row["updated_at"]),
            closed_at=str_to_dt(row["closed_at"]),
        )
