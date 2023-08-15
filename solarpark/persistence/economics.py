# pylint: disable=singleton-comparison,W0622
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from solarpark.models.economics import (
    DividendCreateRequest,
    DividendUpdateRequest,
    MemberEconomicsCreateRequest,
    MemberEconomicsUpdateRequest,
    PaymentCreateRequest,
    PaymentUpdateRequest,
)
from solarpark.persistence.models.economics import Dividend, MemberEconomics, Payment


def create_member_economics(db: Session, member_economics_request: MemberEconomicsCreateRequest):
    member_economics = MemberEconomics(
        member_id=member_economics_request.member_id,
        nr_of_shares=member_economics_request.nr_of_shares,
        total_investment=member_economics_request.total_investment,
        current_value=member_economics_request.total_investment,
        reinvested=member_economics_request.reinvested,
        account_balance=member_economics_request.account_balance,
        pay_out=member_economics_request.pay_out,
        disbursed=member_economics_request.disbursed,
    )
    db.add(member_economics)
    db.commit()
    db.refresh(member_economics)
    return member_economics


def get_member_economics(db: Session, economics_id: int):
    result = db.query(MemberEconomics).filter(MemberEconomics.id == economics_id).all()
    return {"data": result, "total": len(result)}


def get_member_economics_by_member(db: Session, member_id: int):
    result = db.query(MemberEconomics).filter(MemberEconomics.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def update_member_economics(db: Session, economics_id: int, economics_update: MemberEconomicsUpdateRequest):
    db.query(MemberEconomics).filter(MemberEconomics.id == economics_id).update(economics_update.dict())
    db.commit()
    return db.query(MemberEconomics).filter(MemberEconomics.id == economics_id).first()


def get_all_members_economics(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(MemberEconomics).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(MemberEconomics)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(MemberEconomics).order_by(MemberEconomics.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }

    return {
        "data": db.query(MemberEconomics).order_by(MemberEconomics.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def delete_member_economics(db: Session, economics_id: int) -> bool:
    deleted = db.query(MemberEconomics).filter(MemberEconomics.id == economics_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def create_dividend(db: Session, dividend_request: DividendCreateRequest):
    dividend = Dividend(
        dividend_per_share=dividend_request.dividend_per_share,
        payment_year=dividend_request.payment_year,
    )
    db.add(dividend)
    db.commit()
    db.refresh(dividend)
    return dividend


def get_dividend_by_id(db: Session, dividend_id: int):
    result = db.query(Dividend).filter(Dividend.id == dividend_id).all()
    return {"data": result, "total": len(result)}


def get_dividend_by_year(db: Session, dividend_year: int):
    result = db.query(Dividend).filter(Dividend.payment_year == dividend_year).all()
    return {"data": result, "total": len(result)}


def update_dividend(db: Session, dividend_id: int, dividend_update: DividendUpdateRequest):
    db.query(Dividend).filter(Dividend.id == dividend_id).update(dividend_update.dict())
    db.commit()
    return db.query(Dividend).filter(Dividend.id == dividend_id).first()


def get_all_dividends(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(Dividend).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(Dividend)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(Dividend).order_by(Dividend.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }

    return {
        "data": db.query(Dividend).order_by(Dividend.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def delete_dividend(db: Session, dividend_id: int) -> bool:
    deleted = db.query(Dividend).filter(Dividend.id == dividend_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


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


def get_payment_by_member_id(db: Session, member_id: int):
    result = db.query(Payment).filter(Payment.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def get_payments_by_year(db: Session, payment_year: int):
    result = db.query(Payment).filter(Payment.year == payment_year).all()
    return {"data": result, "total": len(result)}


def update_payment_by_member_id(db: Session, member_id: int, payment_update: PaymentUpdateRequest):
    db.query(Payment).filter(Payment.member_id == member_id).update(payment_update.dict())
    db.commit()
    return db.query(Payment).filter(Payment.member_id == member_id).first()
