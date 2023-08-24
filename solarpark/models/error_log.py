from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ErrorLog(BaseModel):
    id: int
    member_id: Optional[int] = None
    share_id: Optional[int] = None
    comment: str
    resolved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ErrorLogCreateRequest(BaseModel):
    member_id: Optional[int] = None
    share_id: Optional[int] = None
    comment: str
    resolved: bool


class ErrorLogUpdateRequest(BaseModel):
    member_id: Optional[int] = None
    share_id: Optional[int] = None
    comment: str
    resolved: bool


class ErrorLogs(BaseModel):
    data: List[ErrorLog]
    total: int

    model_config = ConfigDict(from_attributes=True)
