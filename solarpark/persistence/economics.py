# pylint: disable=singleton-comparison,W0622
from typing import Dict, List

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from solarpark.models.economics import EconomicsCreateRequest, EconomicsUpdateRequest
from solarpark.persistence.models.economics import Economics


def create_economics(db: Session, economics_request: EconomicsCreateRequest):
    economics = Economics(
        member_id=economics_request.member_id,
        nr_of_shares=economics_request.nr_of_shares,
        total_investment=economics_request.total_investment,
        current_value=economics_request.total_investment,
        reinvested=economics_request.reinvested,
        account_balance=economics_request.account_balance,
        pay_out=economics_request.pay_out,
        disbursed=economics_request.disbursed,
    )
    db.add(economics)
    db.commit()
    db.refresh(economics)
    return economics


def get_economics(db: Session, economics_id: int):
    result = db.query(Economics).filter(Economics.id == economics_id).all()
    return {"data": result, "total": len(result)}


def get_economics_by_list_ids(db: Session, economics_ids: list):
    result = db.query(Economics).filter(Economics.id.in_(economics_ids)).all()
    return {"data": result, "total": len(result)}


def get_economics_by_member(db: Session, member_id: int):
    result = db.query(Economics).filter(Economics.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def update_economics(db: Session, economics_id: int, economics_update: EconomicsUpdateRequest):
    db.query(Economics).filter(Economics.id == economics_id).update(economics_update.model_dump())
    db.commit()
    return db.query(Economics).filter(Economics.id == economics_id).first()


def get_all_economics(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(Economics).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(Economics)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(Economics).order_by(Economics.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }

    return {
        "data": db.query(Economics).order_by(Economics.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def delete_economics(db: Session, economics_id: int) -> bool:
    deleted = db.query(Economics).filter(Economics.id == economics_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def delete_economics_by_member(db: Session, member_id: int) -> bool:
    deleted = db.query(Economics).filter(Economics.member_id == member_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def get_total_disbursed(db: Session):
    return int(db.query(func.sum(Economics.disbursed)).scalar())


def get_total_account_balance(db: Session):
    return int(db.query(func.sum(Economics.account_balance)).scalar())
