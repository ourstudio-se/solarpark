from typing import List, Optional

from pydantic import BaseModel


class MemberEconomics(BaseModel):
    id: int
    member_id: int
    nr_of_shares: Optional[int]
    total_investment: Optional[int]
    current_value: Optional[int]
    reinvested: Optional[int]
    account_balance: Optional[int]
    pay_out: Optional[bool]
    disbursed: Optional[int]

    class Config:
        orm_mode = True


class MembersEconomics(BaseModel):
    data: List[MemberEconomics]
    total: int

    class Config:
        orm_mode = True


class MemberEconomicsCreateRequest(BaseModel):
    member_id: int
    nr_of_shares: Optional[int]
    total_investment: Optional[int]
    current_value: Optional[int]
    reinvested: Optional[int]
    account_balance: Optional[int]
    pay_out: Optional[bool]
    disbursed: Optional[int]


class MemberEconomicsUpdateRequest(BaseModel):
    nr_of_shares: Optional[int]
    total_investment: Optional[int]
    current_value: Optional[int]
    reinvested: Optional[int]
    account_balance: Optional[int]
    pay_out: Optional[bool]
    disbursed: Optional[int]


class Dividend(BaseModel):
    id: int
    dividend_per_share: Optional[int]
    payment_year: Optional[int]

    class Config:
        orm_mode = True


class Dividends(BaseModel):
    data: List[Dividend]
    total: int

    class Config:
        orm_mode = True


class DividendCreateRequest(BaseModel):
    dividend_per_share: Optional[int]
    payment_year: Optional[int]


class DividendUpdateRequest(BaseModel):
    dividend_per_share: Optional[int]
    payment_year: Optional[int]


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
