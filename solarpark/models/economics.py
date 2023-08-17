from typing import List, Optional

from pydantic import BaseModel


class EconomicsMember(BaseModel):
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


class Economics(BaseModel):
    data: List[EconomicsMember]
    total: int

    class Config:
        orm_mode = True


class EconomicsCreateRequest(BaseModel):
    member_id: int
    nr_of_shares: Optional[int]
    total_investment: Optional[int]
    current_value: Optional[int]
    reinvested: Optional[int]
    account_balance: Optional[int]
    pay_out: Optional[bool]
    disbursed: Optional[int]


class EconomicsUpdateRequest(BaseModel):
    nr_of_shares: Optional[int]
    total_investment: Optional[int]
    current_value: Optional[int]
    reinvested: Optional[int]
    account_balance: Optional[int]
    pay_out: Optional[bool]
    disbursed: Optional[int]
