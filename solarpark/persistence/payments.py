# pylint: disable=singleton-comparison,W0622


from datetime import datetime
from typing import Dict, List

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from solarpark.models.payments import PaymentCreateRequest, PaymentUpdateRequest
from solarpark.persistence.models.payments import Payment


def create_payment(db: Session, payment_request: PaymentCreateRequest):
    payment = Payment(
        member_id=payment_request.member_id,
        year=payment_request.year,
        amount=payment_request.amount,
        paid_out=payment_request.paid_out,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_id(db: Session, payment_id: int):
    result = db.query(Payment).filter(Payment.id == payment_id).all()
    return {"data": result, "total": len(result)}


def get_payment_by_list_ids(db: Session, payment_ids: list):
    result = db.query(Payment).filter(Payment.id.in_(payment_ids)).all()
    return {"data": result, "total": len(result)}


def get_payment_by_member_id(db: Session, member_id: int):
    result = db.query(Payment).filter(Payment.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def get_payments_by_year(db: Session, payment_year: int):
    result = db.query(Payment).filter(Payment.year == payment_year).all()
    return {"data": result, "total": len(result)}


def update_payment_id(db: Session, payment_id: int, payment_update: PaymentUpdateRequest):
    db.query(Payment).filter(Payment.id == payment_id).update(payment_update.model_dump())
    db.commit()
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_all_payments(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(Payment).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(Payment)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }  # noqa: E731

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(Payment).order_by(Payment.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }

    return {
        "data": db.query(Payment).order_by(Payment.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def delete_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    deleted = db.query(Payment).filter(Payment.id == payment_id).delete()
    if deleted == 1:
        db.commit()
        return payment
    return False


def get_year_payments(db: Session):
    return (
        db.query(func.sum(Payment.amount))
        .filter(Payment.year == datetime.now().year)
        .filter(Payment.paid_out != True)  # noqa: E712
        .scalar()
    )
