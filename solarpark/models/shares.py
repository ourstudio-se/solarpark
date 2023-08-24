from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Share(BaseModel):
    id: int
    comment: Optional[str] = None
    purchased_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_id: int
    initial_value: float
    current_value: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ShareResponse(BaseModel):
    data: List[Share]
    total: int


class ShareCreateRequestImport(BaseModel):
    id: int
    comment: Optional[str] = None
    purchased_at: datetime
    member_id: int
    initial_value: float
    current_value: float


class Shares(BaseModel):
    data: List[Share]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ShareUpdateRequest(BaseModel):
    comment: Optional[str] = None
    purchased_at: datetime
    member_id: int
    initial_value: float
    current_value: float


class ShareCreateRequest(BaseModel):
    comment: Optional[str] = None
    purchased_at: datetime
    member_id: int
    initial_value: float
