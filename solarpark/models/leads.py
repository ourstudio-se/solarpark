from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from solarpark.persistence.database import utcnow


class Lead(BaseModel):
    id: int
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birth_date: Optional[datetime] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    zip_code: Optional[str] = None
    locality: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    existing_id: Optional[int] = None
    quantity_shares: int
    generate_certificate: Optional[bool] = False
    purchased_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SingleLead(BaseModel):
    data: Lead

    model_config = ConfigDict(from_attributes=True)


class Leads(BaseModel):
    data: List[Lead]
    total: int

    model_config = ConfigDict(from_attributes=True)


class LeadCreateRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birth_date: Optional[datetime] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    zip_code: Optional[str] = None
    locality: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    existing_id: Optional[int] = None
    quantity_shares: int
    generate_certificate: bool = False
    purchased_at: datetime = utcnow()


class LeadUpdateRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birth_date: Optional[datetime] = None
    org_name: Optional[str] = None
    org_number: Optional[str] = None
    street_address: Optional[str] = None
    zip_code: Optional[str] = None
    locality: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    existing_id: Optional[int] = None
    quantity_shares: int
    generate_certificate: Optional[bool] = None
    purchased_at: datetime
