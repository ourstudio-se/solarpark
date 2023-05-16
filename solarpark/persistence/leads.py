# pylint: disable=W0511
from datetime import datetime
from typing import Dict

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
    return None
