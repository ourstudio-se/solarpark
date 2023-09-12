# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.members import MemberCreateRequest, Members, MemberUpdateRequest, SingleMember
from solarpark.persistence import delete_all_member_data
from solarpark.persistence.database import get_db
from solarpark.persistence.members import (
    create_member,
    find_member,
    get_all_members,
    get_member,
    get_member_by_list_ids,
    update_member,
)

router = APIRouter()


@router.get("/members/{member_id}", summary="Get member")
async def get_member_endpoint(member_id: int, db: Session = Depends(get_db)) -> SingleMember:
    members = get_member(db, member_id)

    if len(members["data"]) != 1:
        raise HTTPException(status_code=404, detail="member not found")

    return {"data": members["data"][0]}


@router.get("/members/search/{term}", summary="Search for member")
async def search_members_endpoint(term: str, db: Session = Depends(get_db)):
    return find_member(db, term)


@router.get("/members", summary="Get all members")
async def get_members_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> Members:
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
                return get_member_by_list_ids(db, filter_obj["id"])
            return get_member(db, filter_obj["id"])
        if filter_obj and "q" in filter_obj:
            return find_member(db, filter_obj["q"])

        return get_all_members(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.put("/members/{member_id}", summary="Update member")
async def update_member_endpoint(
    member_id: int, member_request: MemberUpdateRequest, db: Session = Depends(get_db)
) -> SingleMember:
    try:
        updated_member = update_member(db, member_id, member_request)
        return {"data": updated_member}
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
        raise HTTPException(status_code=400, detail="error updating member") from ex


@router.post("/members", summary="Create member")
async def create_member_endpoint(member_request: MemberCreateRequest, db: Session = Depends(get_db)) -> SingleMember:
    try:
        member = create_member(db, member_request)
        return {"data": member}
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
        raise HTTPException(status_code=400, detail="error creating member") from ex


@router.delete("/members/{member_id}", summary="Delete member")
async def delete_member_endpoint(member_id: int, db: Session = Depends(get_db)) -> SingleMember:

    member_deleted = delete_all_member_data(db, member_id)

    if member_deleted:
        return {"data": member_deleted}

    raise HTTPException(status_code=400, detail="member not deleted")
