# pylint: disable=W0511
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.leads import Lead, LeadCreateRequest, Leads
from solarpark.persistence.database import get_db
from solarpark.persistence.leads import create_lead, delete_lead, get_all_leads, get_lead

router = APIRouter()


@router.get("/leads/{lead_id}", summary="Get lead")
async def get_member_endpoint(lead_id: int) -> Lead:  # lead_id: int, db: Session = Depends(get_db)
    leads = get_lead(lead_id)  # db, lead_id

    if leads["data"]:
        lead = leads["data"]
        return lead


@router.get("/leads", summary="Get all leads")
async def get_leads_endpoint() -> Leads:  # db: Session = Depends(get_db)
    leads = get_all_leads()  # db

    if len(leads["data"]) < 1:
        raise HTTPException(status_code=404, detail="leads not found")

    return leads


@router.post("/leads", summary="Create lead")
async def create_lead_endpoint(lead_request: LeadCreateRequest, db: Session = Depends(get_db)) -> Lead:
    try:
        return create_lead(db, lead_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(status_code=400, detail=parse_integrity_error_msg("Key (.*?) exists", str(ex))) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400, detail=parse_integrity_error_msg("Key (.*?) not present", str(ex))
            ) from ex
        raise HTTPException(status_code=400, detail="error creating lead") from ex


@router.delete("/lead/{lead_id}", summary="Delete member")
async def delete_lead_endpoint():  # lead_id: int, db: Session = Depends(get_db)
    lead_deleted = delete_lead()  # db, lead_id

    if lead_deleted:
        return {"detail": "lead deleted successfully"}

    return {"detail": "lead not deleted"}
