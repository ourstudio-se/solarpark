# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.members import Member, MemberCreateRequest, Members, MemberUpdateRequest, MemberWithShares
from solarpark.persistence.database import get_db
from solarpark.persistence.members import (
    create_member,
    delete_member,
    find_member,
    get_all_members,
    get_member,
    update_member,
)
from solarpark.persistence.shares import delete_shares_by_member, get_shares_by_member

router = APIRouter()


@router.get("/members/{member_id}", summary="Get member")
async def get_member_endpoint(member_id: int, db: Session = Depends(get_db)) -> MemberWithShares:
    members = get_member(db, member_id)
    shares = get_shares_by_member(db, member_id)

    if len(members["data"]) != 1:
        raise HTTPException(status_code=404, detail="member not found")

    member = members["data"][0]
    if shares:
        member.shares = shares["data"]

    return member


@router.get("/members/search/{term}", summary="Search for member")
async def search_members_endpoint(term: str, db: Session = Depends(get_db)):
    return find_member(db, term)


@router.get("/members", summary="Get all members")
async def get_members_endpoint(
    range: str | None = None, sort: str | None = None, filter: str | None = None, db: Session = Depends(get_db)
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
                return get_member(db, filter_obj["id"][0])
            return get_member(db, filter_obj["id"])
        if filter_obj and "q" in filter_obj:
            return find_member(db, filter_obj["q"])

        return get_all_members(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.put("/members/{member_id}", summary="Update member")
async def update_member_endpoint(
    member_id: int, member_request: MemberUpdateRequest, db: Session = Depends(get_db)
) -> Member:
    try:
        return update_member(db, member_id, member_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(status_code=400, detail=parse_integrity_error_msg("Key (.*?) exists", str(ex))) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400, detail=parse_integrity_error_msg("Key (.*?) not present", str(ex))
            ) from ex
        raise HTTPException(status_code=400, detail="error updating member") from ex


@router.post("/members", summary="Create member")
async def create_member_endpoint(member_request: MemberCreateRequest, db: Session = Depends(get_db)) -> Member:
    try:
        return create_member(db, member_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(status_code=400, detail=parse_integrity_error_msg("Key (.*?) exists", str(ex))) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400, detail=parse_integrity_error_msg("Key (.*?) not present", str(ex))
            ) from ex
        raise HTTPException(status_code=400, detail="error creating member") from ex


@router.delete("/members/{member_id}", summary="Delete member")
async def delete_member_endpoint(member_id: int, db: Session = Depends(get_db)):
    member_deleted = delete_member(db, member_id)
    shares_deleted = delete_shares_by_member(db, member_id)

    if member_deleted and shares_deleted:
        return {"detail": "member and shares deleted successfully"}
    if shares_deleted:
        return {"detail": "only shares deleted successfully"}
    if member_deleted:
        return {"detail": "member deleted successfully"}
    return {"detail": "no member nor shares deleted"}
