from pydantic import BaseModel, Field


class GetRecoveryCaseInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class GetPaymentInput(BaseModel):
    payment_id: str = Field(..., min_length=1)


class GetOrderInput(BaseModel):
    order_id: str = Field(..., min_length=1)


class GetPaymentLinkInput(BaseModel):
    payment_link_id: str = Field(..., min_length=1)


class GetCustomerContextInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class GetRecoveryHistoryInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class GetSystemHealthInput(BaseModel):
    pass


class AssessRecoveryCaseInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class AnalyzeRootCauseInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class RankInterventionsInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class CreatePaymentLinkInput(BaseModel):
    case_id: str = Field(..., min_length=1)
    action_id: str = Field(..., min_length=1)


class SendPaymentLinkNotificationInput(BaseModel):
    case_id: str = Field(..., min_length=1)
    action_id: str = Field(..., min_length=1)
    medium: str = Field(..., pattern="^(sms|email)$")


class CancelPaymentLinkInput(BaseModel):
    case_id: str = Field(..., min_length=1)
    action_id: str = Field(..., min_length=1)
    payment_link_id: str = Field(..., min_length=1)


class EscalateRecoveryCaseInput(BaseModel):
    case_id: str = Field(..., min_length=1)
    reason_code: str = Field(..., min_length=1)
