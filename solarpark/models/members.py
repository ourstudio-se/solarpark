from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from solarpark.models.shares import Share


class Member(BaseModel):
    id: int
    firstname: str
    lastname: str
    year: int
    birth_date: int
    street_address: str
    zip_code: int
    telephone: Optional[str]
    email: str
    bank: Optional[str]
    swish: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class MemberWithShares(Member):
    shares: Optional[List[Share]]

    class Config:
        orm_mode = True


class MemberCreateRequest(BaseModel):
    id: int
    firstname: str
    lastname: str
    year: int
    birth_date: int
    street_address: str
    zip_code: int
    telephone: Optional[str]
    email: str
    bank: Optional[str]
    swish: Optional[str]


class MemberUpdateRequest(BaseModel):
    firstname: str
    lastname: str
    year: int
    birth_date: int
    street_address: str
    zip_code: int
    telephone: Optional[str]
    email: str
    bank: Optional[str]
    swish: Optional[str]


class Members(BaseModel):
    members: List[Member]

    class Config:
        orm_mode = True
