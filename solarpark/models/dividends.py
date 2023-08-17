from typing import List, Optional

from pydantic import BaseModel


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