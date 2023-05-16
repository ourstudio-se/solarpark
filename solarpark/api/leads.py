# pylint: disable=W0511
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from solarpark.models.leads import Lead, Leads
from solarpark.persistence.database import get_db
from solarpark.persistence.leads import delete_lead, get_all_leads, get_lead

router = APIRouter()


@router.get("/leads/{lead_id}", summary="Get lead")
async def get_member_endpoint(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    leads = get_lead(db, lead_id)

    if leads["data"]:
        lead = leads["data"]
        return lead


@router.get("/leads", summary="Get all leads")
async def get_leads_endpoint(db: Session = Depends(get_db)) -> Leads:
    leads = get_all_leads(db)

    if len(leads["data"]) < 1:
        raise HTTPException(status_code=404, detail="leads not found")

    return leads


@router.delete("/lead/{lead_id}", summary="Delete member")
async def delete_lead_endpoint(lead_id: int, db: Session = Depends(get_db)):
    lead_deleted = delete_lead(db, lead_id)

    if lead_deleted:
        return {"detail": "lead deleted successfully"}

    return {"detail": "lead not deleted"}
