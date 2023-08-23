from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class EconomicsMember(BaseModel):
    id: int
    member_id: int
    nr_of_shares: Optional[int] = None
    total_investment: Optional[float] = None
    current_value: Optional[float] = None
    reinvested: Optional[float] = None
    account_balance: Optional[float] = None
    pay_out: bool
    disbursed: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class Economics(BaseModel):
    data: List[EconomicsMember]
    total: int

    model_config = ConfigDict(from_attributes=True)


class EconomicsCreateRequest(BaseModel):
    member_id: int
    nr_of_shares: Optional[int] = None
    total_investment: Optional[float] = None
    current_value: Optional[float] = None
    reinvested: Optional[float] = None
    account_balance: Optional[float] = None
    pay_out: bool
    disbursed: Optional[float] = None


class EconomicsUpdateRequest(BaseModel):
    nr_of_shares: Optional[int] = None
    total_investment: Optional[float] = None
    current_value: Optional[float] = None
    reinvested: Optional[float] = None
    account_balance: Optional[float] = None
    pay_out: Optional[bool] = None
    disbursed: Optional[float] = None
