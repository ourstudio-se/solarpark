from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from solarpark.models.shares import Share


class Member(BaseModel):
    id: int
    bank: Optional[str] = None
    birth_date: datetime
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    swish: Optional[str] = None
    telephone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    zip_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MemberWithShares(Member):
    shares: Optional[List[Share]]

    model_config = ConfigDict(from_attributes=True)


class MemberCreateRequest(BaseModel):
    bank: Optional[str] = None
    birth_date: datetime
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    swish: Optional[str] = None
    telephone: Optional[str] = None
    created_at: datetime
    zip_code: Optional[str] = None


class MemberUpdateRequest(BaseModel):
    bank: Optional[str] = None
    birth_date: datetime
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    swish: Optional[str]
    telephone: Optional[str]
    zip_code: Optional[str] = None


class Members(BaseModel):
    data: List[Member]
    total: int

    model_config = ConfigDict(from_attributes=True)
