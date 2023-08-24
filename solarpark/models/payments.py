from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Payment(BaseModel):
    id: int
    member_id: int
    year: int
    amount: float
    paid_out: bool

    model_config = ConfigDict(from_attributes=True)


class Payments(BaseModel):
    data: List[Payment]
    total: int

    model_config = ConfigDict(from_attributes=True)


class PaymentCreateRequest(BaseModel):
    member_id: int
    year: int
    amount: float
    paid_out: Optional[bool] = False


class PaymentUpdateRequest(BaseModel):
    year: int
    amount: float
    paid_out: bool
