# pylint: disable=W0511, W0622, R0914, R1721, W0707,R1731
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.dividends import Dividend, DividendCreateRequest, Dividends, DividendUpdateRequest
from solarpark.persistence import make_dividend
from solarpark.persistence.database import get_db
from solarpark.persistence.dividends import (
    create_dividend,
    delete_dividend,
    get_all_dividends,
    get_dividend_by_id,
    get_dividend_by_year,
    update_dividend,
)
from solarpark.persistence.economics import get_all_economics

router = APIRouter()


@router.post("/dividends", summary="Create dividend")
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


@router.get("/dividends/{dividend_id}", summary="Get dividend")
async def get_dividend_endpoint(dividend_id: int, db: Session = Depends(get_db)) -> Dividend:
    dividends = get_dividend_by_id(db, dividend_id)

    if len(dividends["data"]) != 1:
        raise HTTPException(status_code=404, detail="dividend not found")

    dividend = dividends["data"][0]

    return dividend


@router.get("/dividends", summary="Get all dividens")
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


@router.put("/dividends/{dividend_id}", summary="Update dividend")
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


@router.delete("/dividends/{dividend_id}", summary="Delete dividend")
async def delete_dividend_endpoint(dividend_id: int, db: Session = Depends(get_db)):
    dividend_deleted = delete_dividend(db, dividend_id)

    if dividend_deleted:
        return {"detail": "dividend deleted successfully"}
    return {"detail": "no dividend deleted"}


@router.put("/dividends/fulfill/{payment_year}", summary="Carry out dividend")
async def make_dividend_endpoint(
    payment_year: int,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    dividend = get_dividend_by_year(db, payment_year)
    if dividend and dividend["data"]:
        if len(dividend["data"]) != 1:
            raise HTTPException(status_code=400, detail="no dividend found or no unique dividend ")
        amount = dividend["data"][0].dividend_per_share
    else:
        raise HTTPException(status_code=400, detail="no dividend found")

    economics = get_all_economics(db, [], [])
    if economics and economics["total"]:
        nr_of_economics = economics["total"]
    else:
        raise HTTPException(status_code=400, detail="economics not found")

    background_tasks.add_task(make_dividend, db, amount, payment_year, nr_of_economics)

    return {"message": "dividend started in the background"}
