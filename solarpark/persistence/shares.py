# pylint: disable=singleton-comparison,W0622

from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from solarpark.models.economics import EconomicsUpdateRequest
from solarpark.models.shares import ShareCreateRequest, ShareCreateRequestImport, ShareUpdateRequest
from solarpark.persistence.economics import get_economics_by_member, update_economics
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


def create_share_import(db: Session, share_request: ShareCreateRequestImport):
    share = Share(
        id=share_request.id,
        member_id=share_request.member_id,
        initial_value=share_request.initial_value,
        current_value=share_request.current_value,
        purchased_at=share_request.purchased_at,
        comment=share_request.comment,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def create_share(db: Session, share_request: ShareCreateRequest):
    share = Share(
        comment=share_request.comment,
        member_id=share_request.member_id,
        initial_value=share_request.initial_value,
        current_value=share_request.initial_value,
        purchased_at=share_request.purchased_at,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def update_share(db: Session, share_id: int, share_update: ShareUpdateRequest):
    share_before_update = get_share(db, share_id)

    if share_before_update["data"][0].member_id == share_update.member_id:
        db.query(Share).filter(Share.id == share_id).update(share_update.dict())
        db.commit()
        return db.query(Share).filter(Share.id == share_id).first()

    members_id = [share_before_update["data"][0].member_id, share_update.member_id]
    db.query(Share).filter(Share.id == share_id).update(share_update.dict())
    db.commit()

    for member_id in members_id:
        shares = get_shares_by_member(db, member_id)
        nr_of_shares = shares["total"]
        total_investment = sum(share.initial_value for share in shares["data"])
        current_value = sum(share.current_value for share in shares["data"])

        member = get_economics_by_member(db, member_id)["data"][0]
        member_economics_request = EconomicsUpdateRequest(
            nr_of_shares=nr_of_shares,
            total_investment=total_investment,
            current_value=current_value,
            reinvested=member.reinvested,
            account_balance=member.account_balance,
            pay_out=member.pay_out,
            disbursed=member.disbursed,
        )
        update_economics(db, member.id, member_economics_request)

    return db.query(Share).filter(Share.id == share_id).first()


def delete_share(db: Session, share_id: int) -> bool:
    deleted = db.query(Share).filter(Share.id == share_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False
