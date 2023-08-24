# pylint: disable=W0511, W0622, R0914, R1721, W0707,R1731
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.economics import Economics, EconomicsCreateRequest, EconomicsMember, EconomicsUpdateRequest
from solarpark.models.shares import ShareCreateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import (
    create_economics,
    delete_economics,
    get_all_economics,
    get_economics,
    get_economics_by_member,
    update_economics,
)
from solarpark.persistence.shares import create_share, get_shares_by_member
from solarpark.settings import settings

router = APIRouter()


@router.post("/economics", summary="Create economics")
async def create_economics_endpoint(
    economics_request: EconomicsCreateRequest,
    db: Session = Depends(get_db),
) -> EconomicsMember:
    try:
        return create_economics(db, economics_request)
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
async def get_economics_endpoint(economics_id: int, db: Session = Depends(get_db)) -> EconomicsMember:
    members_economics = get_economics(db, economics_id)

    if len(members_economics["data"]) != 1:
        raise HTTPException(status_code=404, detail="member economics not found")

    member_economics = members_economics["data"][0]

    return member_economics


@router.put("/economics/{economics_id}", summary="Update member economics")
async def update_economics_endpoint(
    economics_id: int,
    economics_request: EconomicsUpdateRequest,
    db: Session = Depends(get_db),
) -> EconomicsMember:
    try:
        return update_economics(db, economics_id, economics_request)
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
                return get_economics(db, filter_obj["id"][0])
            return get_economics(db, filter_obj["id"])
        if filter_obj and "member_id" in filter_obj:
            return get_economics_by_member(db, filter_obj["member_id"])

        return get_all_economics(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.delete("/economics/{economics_id}", summary="Delete economics")
async def delete_member_endpoint(economics_id: int, db: Session = Depends(get_db)):
    economics_deleted = delete_economics(db, economics_id)

    if economics_deleted:
        return {"detail": "member economics deleted successfully"}
    return {"detail": "no member economics deleted"}


@router.post("/economics/reinvest", summary="Reinvest for account balance > share price")
async def reinvest_dividend_endpoint(db: Session = Depends(get_db)):
    try:
        members_economics = get_all_economics(db, [], [])["data"]

        for member in members_economics:
            nr_reinvest_shares = int(member.account_balance // settings.SHARE_PRICE)
            for _ in range(nr_reinvest_shares):
                # Lagt till temporär kommentar kanske vill ha ett separat fält sen som i excel?
                share_create_request = ShareCreateRequest(
                    comment="Köpt från konto",
                    date=int(datetime.now().strftime("%Y%m%d")[2:]),
                    member_id=member.member_id,
                    initial_value=settings.SHARE_PRICE,
                )
                create_share(db, share_create_request)

            # Update member_economics
            shares = get_shares_by_member(db, member.member_id)
            nr_of_shares = shares["total"]
            total_investment = sum(share.initial_value for share in shares["data"])
            current_value = sum(share.current_value for share in shares["data"])
            account_balance = member.account_balance - nr_reinvest_shares * settings.SHARE_PRICE
            disbursed = member.disbursed
            reinvested = member.reinvested + nr_reinvest_shares * settings.SHARE_PRICE

            member_economics_request = EconomicsUpdateRequest(
                nr_of_shares=nr_of_shares,
                total_investment=total_investment,
                current_value=current_value,
                reinvested=reinvested,
                account_balance=account_balance,
                pay_out=member.pay_out,
                disbursed=disbursed,
            )

            update_economics(db, member.id, member_economics_request)

        return {"detail": "reinvestment successfully completed"}

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
        raise HTTPException(status_code=400, detail="no reinvestment executed") from ex
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"no reinvestment executed, error:{ex}")
