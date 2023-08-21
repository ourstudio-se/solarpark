from typing import List, Optional

from pydantic import BaseModel


class Share(BaseModel):
    id: int
    comment: Optional[str]
    date: Optional[int]
    member_id: int
    initial_value: int
    current_value: Optional[int]

    class Config:
        from_attributes = True


class ShareResponse(BaseModel):
    data: List[Share]
    total: int


class ShareCreateRequest_csv(BaseModel):
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
        from_attributes = True


class ShareUpdateRequest(BaseModel):
    comment: Optional[str]
    date: Optional[int]
    member_id: Optional[int]
    initial_value: Optional[int]
    current_value: Optional[int]


class ShareCreateRequest(BaseModel):
    comment: Optional[str]
    date: Optional[int]
    member_id: int
    initial_value: int
