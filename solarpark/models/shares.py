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
    from_internal_account: bool

    model_config = ConfigDict(from_attributes=True)


class SingleShare(BaseModel):
    data: Share

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
    from_internal_account: bool


class Shares(BaseModel):
    data: List[Share]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ShareUpdateRequest(BaseModel):
    comment: Optional[str] = None
    purchased_at: datetime
    member_id: int
    current_value: float
    from_internal_account: bool


class ShareCreateRequest(BaseModel):
    comment: Optional[str] = None
    purchased_at: datetime
    member_id: int
    initial_value: float
    from_internal_account: bool
