from typing import List, Optional

from pydantic import BaseModel

from solarpark.models.shares import Share


class Member(BaseModel):
    id: int
    bank: Optional[str]
    birth_date: Optional[int]
    email: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    org_name: Optional[str]
    org_number: Optional[str]
    street_address: Optional[str]
    swish: Optional[str]
    telephone: Optional[str]
    year: Optional[int]
    zip_code: Optional[int]

    class Config:
        from_attributes = True


class MemberWithShares(Member):
    shares: Optional[List[Share]]

    class Config:
        from_attributes = True


class MemberCreateRequest(BaseModel):
    bank: Optional[str]
    birth_date: Optional[int]
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    org_name: Optional[str]
    org_number: Optional[str]
    street_address: str
    swish: Optional[str]
    telephone: Optional[str]
    year: int
    zip_code: int


class MemberUpdateRequest(BaseModel):
    bank: Optional[str]
    birth_date: Optional[int]
    email: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    org_name: Optional[str]
    org_number: Optional[str]
    street_address: Optional[str]
    swish: Optional[str]
    telephone: Optional[str]
    year: Optional[int]
    zip_code: Optional[int]


class Members(BaseModel):
    data: List[Member]
    total: int

    class Config:
        from_attributes = True
