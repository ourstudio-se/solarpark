# pylint: disable=singleton-comparison,W0622
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from solarpark.models.error_log import ErrorLogCreateRequest, ErrorLogUpdateRequest
from solarpark.persistence.models.error_log import ErrorLog


def get_error(db: Session, error_id: int):
    result = db.query(ErrorLog).filter(ErrorLog.id == error_id).all()
    return {"data": result, "total": len(result)}


def get_error_by_list_ids(db: Session, error_ids: list):
    result = db.query(ErrorLog).filter(ErrorLog.id.in_(error_ids)).all()
    return {"data": result, "total": len(result)}


def get_all_errors(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(ErrorLog).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(ErrorLog)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(ErrorLog).order_by(ErrorLog.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }
    return {
        "data": db.query(ErrorLog).order_by(ErrorLog.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def update_error(db: Session, error_id: int, error_update: ErrorLogUpdateRequest):
    db.query(ErrorLog).filter(ErrorLog.id == error_id).update(error_update.model_dump())
    db.commit()
    return db.query(ErrorLog).filter(ErrorLog.id == error_id).first()


def delete_error(db: Session, error_id: int):
    errorlog = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
    deleted = db.query(ErrorLog).filter(ErrorLog.id == error_id).delete()
    if deleted == 1:
        db.commit()
        return errorlog
    return False


def create_error(db: Session, error_request: ErrorLogCreateRequest):
    error = ErrorLog(
        member_id=error_request.member_id,
        share_id=error_request.share_id,
        comment=error_request.comment,
        resolved=error_request.resolved,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error


def get_all_unresolved_errors(db: Session):
    return db.query(ErrorLog).filter(ErrorLog.resolved != True).count()  # noqa: E712
