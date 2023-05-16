from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Share(BaseModel):
    id: int
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    date: int
    member_id: int
    initial_value: int
    current_value: int

    class Config:
        orm_mode = True


class ShareResponse(BaseModel):
    data: List[Share]
    total: int


class ShareResponseTest(Share):
    class Config:
        orm_mode = True


class ShareCreateRequest(BaseModel):
    id: int
    comment: Optional[str]
    date: int
    member_id: int
    initial_value: int
    current_value: int


class Shares(BaseModel):
    data: List[Share]
    total: int

    class Config:
        orm_mode = True


class ShareUpdateRequest(BaseModel):
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    date: int
    member_id: int
    initial_value: int
    current_value: int
