from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Dividend(BaseModel):
    id: int
    dividend_per_share: float
    payment_year: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SingleDividend(BaseModel):
    data: Dividend

    model_config = ConfigDict(from_attributes=True)


class Dividends(BaseModel):
    data: List[Dividend]
    total: int

    model_config = ConfigDict(from_attributes=True)


class DividendCreateRequest(BaseModel):
    dividend_per_share: float
    payment_year: int
    completed: bool = False


class DividendUpdateRequest(BaseModel):
    dividend_per_share: int
    payment_year: int
    completed: bool
