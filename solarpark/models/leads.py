from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Test för att implementera tabell på klienten
# Ändra senare till objekt av memeber och share, för att underlätta dataflytt i databas
class Lead(BaseModel):
    id: int
    birth_date: Optional[int]
    created_at: datetime
    email: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    company_name: Optional[str]
    org_number: Optional[str]
    shares: int

    class Config:
        orm_mode = True


class Leads(BaseModel):
    data: List[Lead]
    total: int

    class Config:
        orm_mode = True
