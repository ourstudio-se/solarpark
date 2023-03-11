from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.members import Member, MemberCreateRequest, Members, MemberUpdateRequest, MemberWithShares
from solarpark.persistence.database import get_db
from solarpark.persistence.members import create_member, delete_member, get_all_members, get_member, update_member
from solarpark.persistence.shares import delete_shares_by_member, get_shares_by_member

router = APIRouter()


@router.get("/members/{member_id}", summary="Get member")
async def get_member_endpoint(member_id: int, db: Session = Depends(get_db)) -> MemberWithShares:
    member = get_member(db, member_id)
    shares = get_shares_by_member(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="member not found")

    if shares:
        member.shares = shares

    return member


@router.get("/members", summary="Get all members")
async def get_members_endpoint(db: Session = Depends(get_db)) -> Members:
    members = get_all_members(db)
    return {"members": members}


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
