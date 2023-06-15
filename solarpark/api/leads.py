# pylint: disable=W0511

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.leads import Lead, LeadCreateRequest, Leads, LeadUpdateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.leads import approve_lead, create_lead, delete_lead, get_all_leads, get_lead, update_lead

router = APIRouter()


@router.get("/leads/{lead_id}", summary="Get lead")
async def get_lead_endpoint(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    leads = get_lead(db, lead_id)

    if len(leads["data"]) != 1:
        raise HTTPException(status_code=404, detail="member not found")

    lead = leads["data"][0]

    return lead


@router.get("/leads", summary="Get all leads")
async def get_leads_endpoint(db: Session = Depends(get_db)) -> Leads:
    return get_all_leads(db)


@router.put("/leads/{lead_id}", summary="Update lead")
async def update_lead_endpoint(lead_id: int, lead_request: LeadUpdateRequest, db: Session = Depends(get_db)) -> Lead:
    try:
        return update_lead(db, lead_id, lead_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) exists", str(ex)),
            ) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) not present", str(ex)),
            ) from ex
        raise HTTPException(status_code=400, detail="error updating lead") from ex


@router.post("/leads", summary="Create lead")
async def create_lead_endpoint(lead_request: LeadCreateRequest, db: Session = Depends(get_db)) -> Lead:
    try:
        return create_lead(db, lead_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) exists", str(ex)),
            ) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) not present", str(ex)),
            ) from ex
        raise HTTPException(status_code=400, detail="error creating lead") from ex


@router.delete("/leads/{lead_id}", summary="Delete lead")
async def delete_lead_endpoint(lead_id: int, db: Session = Depends(get_db)):
    lead_deleted = delete_lead(db, lead_id)

    if lead_deleted:
        return {"detail": "lead deleted successfully"}

    return {"detail": "lead not deleted"}


@router.post("/leads/{lead_id}", summary="Approve leads")
async def test_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    approved: bool = False,
    comment: str = "",
):
    handled_lead = approve_lead(db, lead_id, approved, comment)
    if handled_lead:
        return {"detail": "lead handled successfully"}
    return {"detail": "lead not handled"}
