# pylint: disable=W0511, W0622, R0914, R1721, W0707,R1731
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.economics import (
    Dividend,
    DividendCreateRequest,
    Dividends,
    DividendUpdateRequest,
    MemberEconomics,
    MemberEconomicsCreateRequest,
    MemberEconomicsUpdateRequest,
    MembersEconomics,
    Payment,
    PaymentCreateRequest,
    Payments,
    PaymentUpdateRequest,
)
from solarpark.models.shares import ShareCreateRequest, ShareUpdateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import (
    create_dividend,
    create_member_economics,
    create_payment,
    delete_dividend,
    delete_member_economics,
    get_all_dividends,
    get_all_members_economics,
    get_dividend_by_id,
    get_dividend_by_year,
    get_member_economics,
    get_payment_by_member_id,
    get_payments_by_year,
    update_dividend,
    update_member_economics,
    update_payment_by_member_id,
)
from solarpark.persistence.shares import create_share, get_shares_by_member, update_share
from solarpark.settings import settings

router = APIRouter()


@router.post("/economics/members", summary="Create member economics")
async def create_member_economics_endpoint(
    member_economics_request: MemberEconomicsCreateRequest,
    db: Session = Depends(get_db),
) -> MemberEconomics:
    try:
        return create_member_economics(db, member_economics_request)
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


@router.get("/economics/members/{economics_id}", summary="Get member economics")
async def get_member_economics_endpoint(economics_id: int, db: Session = Depends(get_db)) -> MemberEconomics:
    members_economics = get_member_economics(db, economics_id)

    if len(members_economics["data"]) != 1:
        raise HTTPException(status_code=404, detail="member economics not found")

    member_economics = members_economics["data"][0]

    return member_economics


@router.put("/economics/members/{economics_id}", summary="Update member economics")
async def update_member_economics_endpoint(
    economics_id: int,
    member_economics_request: MemberEconomicsUpdateRequest,
    db: Session = Depends(get_db),
) -> MemberEconomics:
    try:
        return update_member_economics(db, economics_id, member_economics_request)
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


@router.get("/economics/members", summary="Get all members economics")
async def get_members_economics_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> MembersEconomics:
    try:
        # Här förstår jag inte
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
                return get_member_economics(db, filter_obj["id"][0])
            return get_member_economics(db, filter_obj["id"])

        return get_all_members_economics(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.delete("/economics/members/{economics_id}", summary="Delete member")
async def delete_member_endpoint(economics_id: int, db: Session = Depends(get_db)):
    economics_deleted = delete_member_economics(db, economics_id)

    if economics_deleted:
        return {"detail": "member economics deleted successfully"}
    return {"detail": "no member economics deleted"}


@router.post("/economics/dividends", summary="Create dividend")
async def create_dividend_endpoint(
    dividend_request: DividendCreateRequest,
    db: Session = Depends(get_db),
) -> Dividend:
    try:
        return create_dividend(db, dividend_request)
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
        raise HTTPException(status_code=400, detail="error creating dividend") from ex


@router.get("/economics/dividends/{dividend_id}", summary="Get dividend")
async def get_dividend_endpoint(dividend_id: int, db: Session = Depends(get_db)) -> Dividend:
    dividends = get_dividend_by_id(db, dividend_id)

    if len(dividends["data"]) != 1:
        raise HTTPException(status_code=404, detail="dividend not found")

    dividend = dividends["data"][0]

    return dividend


@router.get("/economics/dividends", summary="Get all dividens")
async def get_dividends_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> Dividends:
    try:
        # Här förstår jag inte
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
                return get_dividend_by_id(db, filter_obj["id"][0])
            return get_dividend_by_id(db, filter_obj["id"])

        return get_all_dividends(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.put("/economics/dividends/{dividend_id}", summary="Update dividend")
async def update_dividend_endpoint(
    dividend_id: int,
    dividend_request: DividendUpdateRequest,
    db: Session = Depends(get_db),
) -> Dividend:
    try:
        return update_dividend(db, dividend_id, dividend_request)
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
        raise HTTPException(status_code=400, detail="error updating dividend") from ex


@router.delete("/economics/dividends/{dividend_id}", summary="Delete dividend")
async def delete_dividend_endpoint(dividend_id: int, db: Session = Depends(get_db)):
    dividend_deleted = delete_dividend(db, dividend_id)

    if dividend_deleted:
        return {"detail": "dividend deleted successfully"}
    return {"detail": "no dividend deleted"}


@router.put("/economics/dividends/fulfill/{payment_year}", summary="Carry out dividend")
async def make_dividend_endpoint(payment_year: int, db: Session = Depends(get_db)):
    try:
        amount = get_dividend_by_year(db, payment_year)["data"][0].dividend_per_share
        # Max 10 från databas (limit(10))?
        # Vad händer om det bryts mitt i? Har bara några blivit uppdaterade?
        members_economics = get_all_members_economics(db, [], [])["data"]

        for member in members_economics:
            shares = get_shares_by_member(db, member.member_id)["data"]
            for share in shares:
                current_value = share.current_value - amount
                if current_value < 0:
                    current_value = 0

                share_request = ShareUpdateRequest(
                    comment=share.comment,
                    date=share.date,
                    member_id=share.member_id,
                    initial_value=share.initial_value,
                    current_value=current_value,
                )
                update_share(db, share.id, share_request)

            shares = get_shares_by_member(db, member.member_id)
            nr_of_shares = shares["total"]
            total_investment = sum(share.initial_value for share in shares["data"])
            current_value = sum(share.current_value for share in shares["data"])
            dividend = amount * nr_of_shares
            account_balance = dividend + member.account_balance
            disbursed = member.disbursed
            reinvested = member.reinvested

            if member.pay_out:
                disbursed = dividend + disbursed + member.account_balance  # member account if user change payout
                account_balance = 0

                payment_create_request = PaymentCreateRequest(
                    member_id=member.member_id,
                    year=datetime.now().year,
                    amount=(dividend + member.account_balance),
                    paid_out=False,
                )
                create_payment(db, payment_create_request)

            member_economics_request = MemberEconomicsUpdateRequest(
                nr_of_shares=nr_of_shares,
                total_investment=total_investment,
                current_value=current_value,
                reinvested=reinvested,
                account_balance=account_balance,
                pay_out=member.pay_out,
                disbursed=disbursed,
            )

            update_member_economics(db, member.id, member_economics_request)

        return {"detail": "dividend successfully completed"}

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
        raise HTTPException(status_code=400, detail="no dividend executed") from ex
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"no dividend executed, error:{ex}")


@router.post("/economics/reinvest", summary="Reinvest for account balance > share price")
async def reinvest_dividend_endpoint(db: Session = Depends(get_db)):
    try:
        members_economics = get_all_members_economics(db, [], [])["data"]

        for member in members_economics:
            nr_reinvest_shares = int(member.account_balance // settings.SHARE_PRICE)
            for _ in range(nr_reinvest_shares):
                # Lagt till temporär kommentar kanske vill ha ett separat fält sen som i excel?
                share_create_request = ShareCreateRequest(
                    comment="From internal account",
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

            member_economics_request = MemberEconomicsUpdateRequest(
                nr_of_shares=nr_of_shares,
                total_investment=total_investment,
                current_value=current_value,
                reinvested=reinvested,
                account_balance=account_balance,
                pay_out=member.pay_out,
                disbursed=disbursed,
            )

            update_member_economics(db, member.id, member_economics_request)

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


@router.post("/economics/payment", summary="Create payment")
async def create_payment_endpoint(
    payment_request: PaymentCreateRequest,
    db: Session = Depends(get_db),
) -> Payment:
    try:
        return create_payment(db, payment_request)
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
        raise HTTPException(status_code=400, detail="error creating payment") from ex


@router.get("/economics/payment/{member_id}", summary="Get payment by member id")
async def get_payment_endpoint(member_id: int, db: Session = Depends(get_db)) -> Payment:
    payments = get_payment_by_member_id(db, member_id)

    if len(payments["data"]) != 1:
        raise HTTPException(status_code=404, detail="payment not found")

    payment = payments["data"][0]

    return payment


@router.get("/economics/payment", summary="Get all payments by year")
async def get_payments_endpoint(
    year: int,
    db: Session = Depends(get_db),
) -> Payments:
    try:
        return get_payments_by_year(db, year)

    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"error:{ex}") from ex


@router.put("/economics/payment/{member_id}", summary="Update payment by member id")
async def update_payment_endpoint(
    member_id: int,
    payment_request: PaymentUpdateRequest,
    db: Session = Depends(get_db),
) -> Payment:
    try:
        return update_payment_by_member_id(db, member_id, payment_request)
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
        raise HTTPException(status_code=400, detail="error updating payment") from ex
