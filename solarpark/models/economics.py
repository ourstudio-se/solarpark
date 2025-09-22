from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class EconomicsMember(BaseModel):
    id: int
    member_id: int
    nr_of_shares: int
    total_investment: float
    current_value: float
    reinvested: Optional[float]
    account_balance: float
    pay_out: bool
    disbursed: Optional[float]
    last_dividend_year: Optional[int]
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
    nr_of_shares: int
    total_investment: float
    current_value: float
    reinvested: Optional[float]
    account_balance: float
    pay_out: bool
    disbursed: Optional[float]
    last_dividend_year: Optional[int]
    issued_dividend: Optional[datetime] = None


class EconomicsUpdateRequest(BaseModel):
    nr_of_shares: int
    total_investment: float
    current_value: float
    reinvested: Optional[float]
    account_balance: float
    pay_out: bool
    disbursed: Optional[float]
    last_dividend_year: Optional[int]
    issued_dividend: Optional[datetime] = None
