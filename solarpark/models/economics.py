from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class EconomicsMember(BaseModel):
    id: int
    member_id: int
    nr_of_shares: Optional[int] = 0
    total_investment: Optional[float] = 0
    current_value: Optional[float] = 0
    reinvested: Optional[float] = 0
    account_balance: Optional[float] = 0
    pay_out: bool
    disbursed: Optional[float] = 0
    last_dividend_year: Optional[int] = 0
    issued_dividend: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SingleEconomics(BaseModel):
    data: EconomicsMember

    model_config = ConfigDict(from_attributes=True)


class Economics(BaseModel):
    data: List[EconomicsMember]
    total: int

    model_config = ConfigDict(from_attributes=True)


class EconomicsCreateRequest(BaseModel):
    member_id: int
    nr_of_shares: Optional[int] = 0
    total_investment: Optional[float] = 0
    current_value: Optional[float] = 0
    reinvested: Optional[float] = 0
    account_balance: Optional[float] = 0
    pay_out: bool
    disbursed: Optional[float] = 0
    last_dividend_year: Optional[int] = 0
    issued_dividend: Optional[datetime] = None


class EconomicsUpdateRequest(BaseModel):
    nr_of_shares: Optional[int] = 0
    total_investment: Optional[float] = 0
    current_value: Optional[float] = 0
    reinvested: Optional[float] = 0
    account_balance: Optional[float] = 0
    pay_out: Optional[bool]
    disbursed: Optional[float] = 0
    last_dividend_year: Optional[int] = 0
    issued_dividend: Optional[datetime] = None
