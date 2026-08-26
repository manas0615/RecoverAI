from dataclasses import dataclass


@dataclass(frozen=True)
class _DomainId:
    """
    Base class for all typed identifiers.
    Ensures that identifiers are non-empty strings.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"{self.__class__.__name__} value must be a string")
        if not self.value.strip():
            raise ValueError(
                f"{self.__class__.__name__} value cannot be empty or whitespace"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MerchantId(_DomainId):
    pass


@dataclass(frozen=True)
class CustomerId(_DomainId):
    pass


@dataclass(frozen=True)
class RevenueEventId(_DomainId):
    pass


@dataclass(frozen=True)
class RecoveryCaseId(_DomainId):
    pass


@dataclass(frozen=True)
class RecoveryActionId(_DomainId):
    pass


@dataclass(frozen=True)
class PolicyDecisionId(_DomainId):
    pass


@dataclass(frozen=True)
class VerificationRecordId(_DomainId):
    pass


@dataclass(frozen=True)
class EvidenceId(_DomainId):
    pass
