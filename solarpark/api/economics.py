# pylint: disable=W0511, W0622, R0914, R1721, W0707,R1731
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.api import parse_integrity_error_msg
from solarpark.models.economics import Economics, EconomicsCreateRequest, EconomicsUpdateRequest, SingleEconomics
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import (
    create_economics,
    delete_economics,
    get_all_economics,
    get_economics,
    get_economics_by_list_ids,
    get_economics_by_member,
    update_economics,
)

router = APIRouter()


@router.post("/economics", summary="Create economics")
async def create_economics_endpoint(
    economics_request: EconomicsCreateRequest,
    db: Session = Depends(get_db),
) -> SingleEconomics:
    try:
        economics = create_economics(db, economics_request)
        return {"data": economics}
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
        raise HTTPException(status_code=400, detail="error creating member economics") from ex


@router.get("/economics/{economics_id}", summary="Get member economics")
async def get_economics_endpoint(economics_id: int, db: Session = Depends(get_db)) -> SingleEconomics:
    members_economics = get_economics(db, economics_id)

    if len(members_economics["data"]) != 1:
        raise HTTPException(status_code=404, detail="member economics not found")

    return {"data": members_economics["data"][0]}


@router.put("/economics/{economics_id}", summary="Update member economics")
async def update_economics_endpoint(
    economics_id: int,
    economics_request: EconomicsUpdateRequest,
    db: Session = Depends(get_db),
) -> SingleEconomics:
    try:
        updated_economics = update_economics(db, economics_id, economics_request)
        return {"data": updated_economics}
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
        raise HTTPException(status_code=400, detail="error updating member economics") from ex


@router.get("/economics", summary="Get all members economics")
async def get_all_economics_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> Economics:
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
                return get_economics_by_list_ids(db, filter_obj["id"])
            return get_economics(db, filter_obj["id"])
        if filter_obj and "member_id" in filter_obj:
            if isinstance(filter_obj["member_id"], int):
                return get_economics_by_member(db, filter_obj["member_id"])
            return Economics(data=[], total=0)

        return get_all_economics(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex
    except Exception as ex:
        get_logger().error(ex)
        raise HTTPException(status_code=400, detail="error retrieving economics") from ex


@router.delete("/economics/{economics_id}", summary="Delete economics")
async def delete_member_endpoint(economics_id: int, db: Session = Depends(get_db)) -> SingleEconomics:
    economics_deleted = delete_economics(db, economics_id)
    if economics_deleted:
        return {"data": economics_deleted}

    raise HTTPException(status_code=400, detail="error deleting economics")
