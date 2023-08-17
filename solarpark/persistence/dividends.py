# pylint: disable=singleton-comparison,W0622
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from solarpark.models.dividends import DividendCreateRequest, DividendUpdateRequest
from solarpark.persistence.models.dividends import Dividend


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
