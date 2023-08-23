from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Share(BaseModel):
    id: int
    comment: Optional[str] = None
    created_at: datetime
    member_id: int
    initial_value: float
    current_value: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ShareResponse(BaseModel):
    data: List[Share]
    total: int


class ShareCreateRequest_csv(BaseModel):
    id: int
    comment: Optional[str] = None
    created_at: datetime
    member_id: int
    initial_value: float
    current_value: float


class Shares(BaseModel):
    data: List[Share]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ShareUpdateRequest(BaseModel):
    comment: Optional[str] = None
    created_at: datetime
    member_id: int
    initial_value: float
    current_value: float


class ShareCreateRequest(BaseModel):
    comment: Optional[str] = None
    created_at: datetime
    member_id: int
    initial_value: float
