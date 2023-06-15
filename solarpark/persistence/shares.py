# pylint: disable=singleton-comparison,W0622

from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from solarpark.models.shares import ShareCreateRequest, ShareCreateRequest_csv, ShareUpdateRequest
from solarpark.persistence.models.shares import Share


def get_all_shares(db: Session, sort: List, range: List) -> Dict:
    # return db.query(Share).all()
    total_count = db.query(Share).count()
    # pages = math.ceil(int(total_count) / per_page)

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(Share)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(Share).order_by(Share.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }

    return {
        "data": db.query(Share).order_by(Share.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def get_share(db: Session, share_id: int):
    result = db.query(Share).filter(Share.id == share_id).all()
    return {"data": result, "total": len(result)}


def get_shares_by_member(db: Session, member_id: int):
    result = db.query(Share).filter(Share.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def count_all_shares(db: Session, filter_on_org: bool = False):
    if filter_on_org:
        return db.query(Share).filter(Share.org_number != None).count()  # noqa: E711
    return db.query(Share).count()


def delete_shares_by_member(db: Session, member_id: int):
    deleted = db.query(Share).filter(Share.member_id == member_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def create_share_csv(db: Session, share_request: ShareCreateRequest_csv):
    share = Share(
        id=share_request.id,
        member_id=share_request.member_id,
        initial_value=share_request.initial_value,
        current_value=share_request.current_value,
        date=share_request.date,
        comment=share_request.comment,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def create_share(db: Session, share_request: ShareCreateRequest):
    share = Share(
        comment=share_request.comment,
        date=share_request.date,
        member_id=share_request.member_id,
        initial_value=share_request.initial_value,
        current_value=share_request.initial_value,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def update_share(db: Session, share_id: int, share_update: ShareUpdateRequest):
    db.query(Share).filter(Share.id == share_id).update(share_update.dict())
    db.commit()
    return db.query(Share).filter(Share.id == share_id).first()
