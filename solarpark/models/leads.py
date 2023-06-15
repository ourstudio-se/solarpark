from typing import List, Optional

from pydantic import BaseModel


class Lead(BaseModel):
    id: int
    firstname: Optional[str]
    lastname: Optional[str]
    birth_date: Optional[int]
    company_name: Optional[str]
    org_number: Optional[str]
    street_address: Optional[str]
    zip_code: Optional[str]
    locality: Optional[str]
    email: Optional[str]
    telephone: Optional[str]
    existing_id: int
    quantity_shares: int
    generate_certificate: Optional[bool] = False

    class Config:
        orm_mode = True


class Leads(BaseModel):
    data: List[Lead]
    total: int

    class Config:
        orm_mode = True


class LeadCreateRequest(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    birth_date: Optional[int]
    company_name: Optional[str]
    org_number: Optional[str]
    street_address: Optional[str]
    zip_code: Optional[str]
    locality: Optional[str]
    email: Optional[str]
    telephone: Optional[str]
    existing_id: int
    quantity_shares: int
    generate_certificate: bool = False


class LeadUpdateRequest(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    birth_date: Optional[int]
    company_name: Optional[str]
    org_number: Optional[int]
    street_address: Optional[str]
    zip_code: Optional[int]
    locality: Optional[str]
    email: Optional[str]
    telephone: Optional[int]
    existing_id: Optional[int]
    quantity_shares: int
    generate_certificate: Optional[bool]
