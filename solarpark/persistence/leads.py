# pylint: disable=W0511
from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from solarpark.models.leads import LeadCreateRequest
from solarpark.persistence.models.leads import Lead

dummy_leads = [
    {
        "id": 1,
        "birth_date": 230516,
        "created_at": datetime.now(),
        "email": "test@test.com",
        "firstname": "Simon",
        "lastname": "Hamberg",
        "shares": 1,
    },
    {
        "id": 2,
        "birth_date": 230516,
        "created_at": datetime.now(),
        "email": "testComp@testComp.com",
        "company_name": "SimonAB",
        "org_number": "1234",
        "shares": 10,
    },
]


def get_lead(lead_id: int):  # db: Session,

    for lead in dummy_leads:
        if lead.get("id") == lead_id:
            result = {"data": lead, "total": len(lead)}

    return result


def get_all_leads() -> Dict:  # db: Session
    return {"data": dummy_leads, "total": len(dummy_leads)}


def delete_lead():  # db, lead_id
    # Todo
    # Ta bort lead från databasen för godkänd/icke godkänd medlem
    # Om godkänd, lägg till i member och share
    return 0


def create_lead(db: Session, lead_request: LeadCreateRequest):
    lead = Lead(
        id=lead_request.id,
        firstname=lead_request.firstname,
        lastname=lead_request.lastname,
        birth_date=lead_request.birth_date,
        company_name=lead_request.company_name,
        street_address=lead_request.street_address,
        zip_code=lead_request.zip_code,
        locality=lead_request.locality,
        email=lead_request.email,
        telephone=lead_request.telephone,
        existing_id=lead_request.existing_id,
        quantity_shares=lead_request.quantity_shares,
        generate_certificate=lead_request.generate_certificate,
        created_at=lead_request.created_at,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
