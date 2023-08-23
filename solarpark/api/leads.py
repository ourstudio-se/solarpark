# pylint: disable=W0511, W0622

import json

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
async def get_leads_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> Leads:
    try:
        filter_obj = {}
        sort_obj = []
        range_obj = []

        if filter:
            filter_obj = json.loads(filter)
        if sort:
            sort_obj = json.loads(sort)
        if range:
            range_obj = json.loads(range)

        if filter_obj and "id" in filter_obj:
            if isinstance(filter_obj["id"], list):
                return get_lead(db, filter_obj["id"][0])
            return get_lead(db, filter_obj["id"])

        return get_all_leads(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


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
async def approve_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    approved: bool = False,
    comment: str = "",
):
    handled_lead = approve_lead(db, lead_id, approved, comment)
    if handled_lead:
        return {"detail": "lead handled successfully"}
    return {"detail": "lead not handled"}
