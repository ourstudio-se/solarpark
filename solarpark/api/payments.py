# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.payments import PaymentCreateRequest, PaymentOne, Payments, PaymentUpdateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.payments import (
    create_payment,
    delete_payment,
    get_all_payments,
    get_payment_by_list_ids,
    get_payment_by_member_id,
    get_payment_id,
    update_payment_id,
)

router = APIRouter()


@router.post("/payments", summary="Create payment")
async def create_payment_endpoint(
    payment_request: PaymentCreateRequest,
    db: Session = Depends(get_db),
) -> PaymentOne:
    try:

        payment = create_payment(db, payment_request)
        return {"data": payment}
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


@router.get("/payments/{payment_id}", summary="Get payment with id")
async def get_payment_endpoint(payment_id: int, db: Session = Depends(get_db)) -> PaymentOne:
    payments = get_payment_id(db, payment_id)

    if len(payments["data"]) != 1:
        raise HTTPException(status_code=404, detail="payment not found")

    return {"data": payments["data"][0]}


@router.get("/payments", summary="Get all payments")
async def get_payments_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> Payments:
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
                return get_payment_by_list_ids(db, filter_obj["id"])
            return get_payment_id(db, filter_obj["id"])
        if filter_obj and "member_id" in filter_obj:
            return get_payment_by_member_id(db, filter_obj["member_id"])
        return get_all_payments(db, sort=sort_obj, range=range_obj)

    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"error:{ex}") from ex


@router.put("/payments/{payment_id}", summary="Update payment")
async def update_payment_endpoint(
    payment_id: int,
    payment_request: PaymentUpdateRequest,
    db: Session = Depends(get_db),
) -> PaymentOne:
    try:
        updated_payment = update_payment_id(db, payment_id, payment_request)
        return {"data": updated_payment}
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


@router.delete("/payments/{payment_id}", summary="Delete payment")
async def delete_payment_endpoint(payment_id: int, db: Session = Depends(get_db)):
    lead_deleted = delete_payment(db, payment_id)

    if lead_deleted:
        return {"data": lead_deleted}

    raise HTTPException(status_code=400, detail="error deleting payment")
