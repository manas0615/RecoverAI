from dataclasses import dataclass
from datetime import datetime

from recoverai.domain.identifiers import CustomerId, MerchantId


@dataclass(frozen=True)
class Customer:
    """
    Represents a customer within the Recovery domain.
    PII is intentionally minimized; contact_reference is an opaque reference
    to merchant-controlled contact information.
    """

    customer_id: CustomerId
    merchant_id: MerchantId
    created_at: datetime
    updated_at: datetime
    display_name: str | None = None
    contact_reference: str | None = None
    external_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.customer_id, CustomerId):
            raise TypeError("customer_id must be a CustomerId")
        if not isinstance(self.merchant_id, MerchantId):
            raise TypeError("merchant_id must be a MerchantId")
        if not self.created_at.tzinfo or not self.updated_at.tzinfo:
            raise ValueError("Timestamps must be timezone-aware")
