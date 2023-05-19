from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Lead(BaseModel):
    id: int
    firstname: Optional[str]  # Optional p.g.a. samma fält för namn och företagsnamn hos solarpark.
    lastname: Optional[str]
    birth_date: Optional[int]
    company_name: Optional[str]
    org_number: Optional[int]
    street_address: str
    zip_code: int
    locality: str
    email: str
    telephone: int
    existing_id: int
    quantity_shares: int
    generate_certificate: bool
    created_at: datetime

    # Gammal modell för dummy data
    """ id: int
    birth_date: Optional[int]
    created_at: datetime
    email: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    company_name: Optional[str]
    org_number: Optional[str]
    shares: int """

    class Config:
        orm_mode = True


class Leads(BaseModel):
    data: List[Lead]
    total: int

    class Config:
        orm_mode = True


class LeadCreateRequest(BaseModel):
    id: int
    firstname: Optional[str]  # Optional p.g.a. samma fält för namn och företagsnamn hos solarpark.
    lastname: Optional[str]
    birth_date: Optional[int]
    company_name: Optional[str]
    org_number: Optional[int]
    street_address: str
    zip_code: int
    locality: str
    email: str
    telephone: int
    existing_id: int
    quantity_shares: int
    generate_certificate: bool
    created_at: datetime
