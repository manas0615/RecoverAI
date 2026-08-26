from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from recoverai.domain.identifiers import MerchantId
from recoverai.domain.money import CurrencyCode


class MerchantStatus(Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class Merchant:
    merchant_id: MerchantId
    display_name: str
    default_currency: CurrencyCode
    status: MerchantStatus
    created_at: datetime
    updated_at: datetime
    external_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.merchant_id, MerchantId):
            raise TypeError("merchant_id must be a MerchantId")
        if not isinstance(self.default_currency, CurrencyCode):
            raise TypeError("default_currency must be a CurrencyCode")
        if not isinstance(self.status, MerchantStatus):
            raise TypeError("status must be a MerchantStatus")
        if not self.created_at.tzinfo or not self.updated_at.tzinfo:
            raise ValueError("Timestamps must be timezone-aware")
