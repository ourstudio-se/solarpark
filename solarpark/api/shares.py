# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.shares import ShareCreateRequest, ShareOne, Shares, ShareUpdateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.shares import (
    create_share,
    delete_share,
    get_all_shares,
    get_share,
    get_share_by_list_ids,
    get_shares_by_member,
    update_share,
)

router = APIRouter()


@router.get("/shares/{share_id}", summary="Get specific share")
async def get_share_endpoint(share_id: int, db: Session = Depends(get_db)) -> ShareOne:
    share = get_share(db, share_id)

    if len(share["data"]) != 1:
        raise HTTPException(status_code=404, detail="share not found")
    return {"data": share["data"][0]}


@router.get("/shares", summary="Get shares")
async def get_shares_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
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
                return get_share_by_list_ids(db, filter_obj["id"])
            return get_share(db, filter_obj["id"])
        if filter_obj and "member_id" in filter_obj:
            return get_shares_by_member(db, filter_obj["member_id"])
        if filter_obj and "q" in filter_obj:
            return get_share(db, filter_obj["q"])

        return get_all_shares(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.post("/shares", summary="Create share")
async def create_share_endpoint(share_request: ShareCreateRequest, db: Session = Depends(get_db)) -> ShareOne:
    try:
        share = create_share(db, share_request)
        return {"data": share}
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
    raise HTTPException(status_code=400, detail="error creating share")


@router.put("/shares/{share_id}", summary="Update share")
async def update_member_endpoint(
    share_id: int, share_request: ShareUpdateRequest, db: Session = Depends(get_db)
) -> ShareOne:
    try:
        updated_share = update_share(db, share_id, share_request)
        return {"data": updated_share}
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
        raise HTTPException(status_code=400, detail="error updating share") from ex


@router.delete("/shares/{share_id}", summary="Delete share")
async def delete_share_endpoint(share_id: int, db: Session = Depends(get_db)) -> ShareOne:
    share_deleted = delete_share(db, share_id)

    if share_deleted:
        return {"data": share_deleted}

    raise HTTPException(status_code=400, detail="error deleting share")
