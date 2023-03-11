from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Share(BaseModel):
    id: int
    member_id: int
    date: int
    created_at: datetime

    class Config:
        orm_mode = True


class ShareCreateRequest(BaseModel):
    id: int
    member_id: int
    date: int
    comment: Optional[str]
