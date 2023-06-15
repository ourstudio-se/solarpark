# pylint: disable=W0511
from typing import Dict

from sqlalchemy.orm import Session

from solarpark.models.leads import LeadCreateRequest, LeadUpdateRequest  # , LeadApproveRequest
from solarpark.models.members import MemberCreateRequest
from solarpark.models.shares import ShareCreateRequest
from solarpark.persistence.members import create_member
from solarpark.persistence.models.leads import Lead
from solarpark.persistence.shares import create_share


def get_lead(db: Session, lead_id: int):
    result = db.query(Lead).filter(Lead.id == lead_id).all()

    return {"data": result, "total": len(result)}


def get_all_leads(db: Session) -> Dict:
    total_count = db.query(Lead).count()

    return {
        "data": db.query(Lead).order_by(Lead.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def delete_lead(db: Session, lead_id):
    deleted = db.query(Lead).filter(Lead.id == lead_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def create_lead(db: Session, lead_request: LeadCreateRequest):
    lead = Lead(
        firstname=lead_request.firstname,
        lastname=lead_request.lastname,
        birth_date=lead_request.birth_date,
        company_name=lead_request.company_name,
        org_number=lead_request.org_number,
        street_address=lead_request.street_address,
        zip_code=lead_request.zip_code,
        locality=lead_request.locality,
        email=lead_request.email,
        telephone=lead_request.telephone,
        existing_id=lead_request.existing_id,
        quantity_shares=lead_request.quantity_shares,
        generate_certificate=lead_request.generate_certificate,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def update_lead(db: Session, lead_id: int, lead_update: LeadUpdateRequest):
    db.query(Lead).filter(Lead.id == lead_id).update(lead_update.dict())
    db.commit()
    return db.query(Lead).filter(Lead.id == lead_id).first()


def approve_lead(db: Session, lead_id: int, approved: bool, comment: str):
    lead = db.query(Lead).filter(Lead.id == lead_id).all()[0]

    if approved:
        existing_member_id = lead.existing_id
        if existing_member_id:
            share_request = ShareCreateRequest(
                comment=comment,
                date=2023,
                member_id=existing_member_id,
                initial_value=3000,
            )
            for _ in range(lead.quantity_shares):
                create_share(db=db, share_request=share_request)

            delete_lead(db, lead_id)
            return True

        member_request = MemberCreateRequest(
            birth_date=lead.birth_date,
            email=lead.email,
            firstname=lead.firstname,
            lastname=lead.lastname,
            org_number=lead.org_number,
            street_address=lead.street_address,
            telephone=lead.telephone,
            year=2023,  # datetime istället
            zip_code=lead.zip_code,
        )
        new_member = create_member(db, member_request)
        new_member_id = new_member.id
        share_request = ShareCreateRequest(
            comment=comment,
            date=2023,
            member_id=new_member_id,
            initial_value=3000,
        )
        for _ in range(lead.quantity_shares):
            create_share(db=db, share_request=share_request)

        delete_lead(db, lead_id)
        return True

    if not approved:
        delete_lead(db, lead_id)
        return True

    return False

    # Todo
    # Ta bort lead från databasen för godkänd/icke godkänd medlem
    # Om godkänd, lägg till i member och share
