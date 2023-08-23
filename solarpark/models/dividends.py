from typing import List

from pydantic import BaseModel, ConfigDict


class Dividend(BaseModel):
    id: int
    dividend_per_share: float
    payment_year: int

    model_config = ConfigDict(from_attributes=True)


class Dividends(BaseModel):
    data: List[Dividend]
    total: int

    model_config = ConfigDict(from_attributes=True)


class DividendCreateRequest(BaseModel):
    dividend_per_share: float
    payment_year: int


class DividendUpdateRequest(BaseModel):
    dividend_per_share: int
    payment_year: int
