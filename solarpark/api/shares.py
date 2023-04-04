# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.shares import Share, ShareCreateRequest, Shares
from solarpark.persistence.database import get_db
from solarpark.persistence.shares import create_share, get_all_shares, get_share, get_shares_by_member

router = APIRouter()


@router.get("/shares/{share_id}", summary="Get specific share")
async def get_share_endpoint(share_id: int, db: Session = Depends(get_db)) -> Share:
    share = get_share(db, share_id)
    if not share:
        raise HTTPException(status_code=404, detail="share not found")
    return share


@router.get("/shares", summary="Get shares")
async def get_shares_endpoint(
    range: str | None = None, sort: str | None = None, filter: str | None = None, db: Session = Depends(get_db)
) -> Shares:
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
                return get_share(db, filter_obj["id"][0])
            return get_share(db, filter_obj["id"])
        if filter_obj and "member_id" in filter_obj:
            return get_shares_by_member(db, filter_obj["member_id"])
        if filter_obj and "q" in filter_obj:
            return get_share(db, filter_obj["q"])

        return get_all_shares(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.post("/shares", summary="Create share")
async def create_share_endpoint(share_request: ShareCreateRequest, db: Session = Depends(get_db)) -> Share:
    try:
        return create_share(db, share_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(status_code=400, detail=parse_integrity_error_msg("Key (.*?) exists", str(ex))) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400, detail=parse_integrity_error_msg("Key (.*?) not present", str(ex))
            ) from ex
    raise HTTPException(status_code=400, detail="error creating share")
