from typing import List, Optional

from pydantic import BaseModel


class Payment(BaseModel):
    id: int
    member_id: int
    year: Optional[int]
    amount: Optional[int]
    paid_out: Optional[bool]

    class Config:
        orm_mode = True


class Payments(BaseModel):
    data: List[Payment]
    total: int

    class Config:
        orm_mode = True


class PaymentCreateRequest(BaseModel):
    member_id: int
    year: int
    amount: int
    paid_out: Optional[bool] = False


class PaymentUpdateRequest(BaseModel):
    year: Optional[int]
    amount: Optional[int]
    paid_out: Optional[bool]
