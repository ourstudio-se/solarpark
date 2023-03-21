from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from solarpark.models.shares import Share


class Member(BaseModel):
    id: int
    bank: Optional[str]
    birth_date: int
    created_at: datetime
    email: str
    firstname: str
    lastname: str
    org_number: Optional[str]
    street_address: str
    swish: Optional[str]
    telephone: Optional[str]
    updated_at: Optional[datetime]
    year: int
    zip_code: int

    class Config:
        orm_mode = True


class MemberWithShares(Member):
    shares: Optional[List[Share]]

    class Config:
        orm_mode = True


class MemberCreateRequest(BaseModel):
    id: int
    bank: Optional[str]
    birth_date: int
    email: str
    firstname: str
    lastname: str
    org_number: Optional[str]
    street_address: str
    swish: Optional[str]
    telephone: Optional[str]
    year: int
    zip_code: int


class MemberUpdateRequest(BaseModel):
    bank: Optional[str]
    birth_date: int
    email: str
    firstname: str
    lastname: str
    org_number: Optional[str]
    street_address: str
    swish: Optional[str]
    telephone: Optional[str]
    year: int
    zip_code: int


class Members(BaseModel):
    members: List[Member]

    class Config:
        orm_mode = True
