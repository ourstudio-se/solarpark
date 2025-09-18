# pylint: disable=singleton-comparison,W0622

from typing import Dict, List

from sqlalchemy import extract, func, text
from sqlalchemy.orm import Session

from solarpark.models.economics import EconomicsUpdateRequest
from solarpark.models.error_log import ErrorLogCreateRequest
from solarpark.models.shares import ShareCreateRequest, ShareCreateRequestImport, ShareUpdateRequest
from solarpark.persistence.economics import get_economics_by_member, update_economics
from solarpark.persistence.error_log import create_error
from solarpark.persistence.models.economics import Economics
from solarpark.persistence.models.members import Member
from solarpark.persistence.models.shares import Share
from solarpark.settings import settings


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


def get_share_by_list_ids(db: Session, share_ids: list):
    result = db.query(Share).filter(Share.id.in_(share_ids)).all()
    return {"data": result, "total": len(result)}


def get_shares_by_member(db: Session, member_id: int):
    result = db.query(Share).filter(Share.member_id == member_id).all()
    return {"data": result, "total": len(result)}


def get_shares_by_member_and_purchase_year(db: Session, member_id: int, year: int):
    result = (
        db.query(Share).filter(Share.member_id == member_id).filter(extract("year", Share.purchased_at) < year).all()
    )
    return {"data": result, "total": len(result)}


def count_all_shares(db: Session):
    all_shares = db.query(Share).filter(Share.member_id != settings.SOLARPARK_MEMBER_ID).count()
    all_solarpark_shares = db.query(Share).filter(Share.member_id == settings.SOLARPARK_MEMBER_ID).count()
    reinvested_shares = db.query(Share).filter(Share.from_internal_account == True).count()  # noqa: E712
    org_more_than_one_share = (
        db.query(Member)
        .join(Share, Member.id == Share.member_id)
        .filter(Member.org_name != None)  # noqa: E711
        .filter(Member.id != settings.SOLARPARK_MEMBER_ID)
        .group_by(Member.id)
        .having(func.count(Share.id) > 1)
        .count()
    )

    return all_shares, all_solarpark_shares, reinvested_shares, org_more_than_one_share


def all_members_with_shares(db: Session):
    org_with_shares = (
        db.query(Member)
        .join(Share, Member.id == Share.member_id)
        .filter(Member.org_name != None)  # noqa: E711
        .filter(Member.id != settings.SOLARPARK_MEMBER_ID)
        .group_by(Member.id)
        .having(func.count(Share.id) > 0)
        .count()
    )

    all_with_shares = (
        db.query(Member)
        .join(Share, Member.id == Share.member_id)
        .group_by(Member.id)
        .filter(Member.id != settings.SOLARPARK_MEMBER_ID)
        .having(func.count(Share.id) > 0)
        .count()
    )

    return all_with_shares, org_with_shares


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
        from_internal_account=share_request.from_internal_account,
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
        from_internal_account=False,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def update_share(db: Session, share_id: int, share_update: ShareUpdateRequest):
    share_before_update = get_share(db, share_id)

    if share_before_update["data"][0].member_id == share_update.member_id:
        db.query(Share).filter(Share.id == share_id).update(share_update.model_dump())
        db.commit()
        return db.query(Share).filter(Share.id == share_id).first()

    members_id = [share_before_update["data"][0].member_id, share_update.member_id]
    db.query(Share).filter(Share.id == share_id).update(share_update.model_dump())
    db.commit()

    for member_id in members_id:
        shares = get_shares_by_member(db, member_id)
        nr_of_shares = shares["total"]
        total_investment = sum(share.initial_value for share in shares["data"])
        current_value = sum(share.current_value for share in shares["data"])

        if member_id == settings.SOLARPARK_MEMBER_ID:
            continue

        member = get_economics_by_member(db, member_id)["data"][0]
        member_economics_request = EconomicsUpdateRequest(
            nr_of_shares=nr_of_shares,
            total_investment=total_investment,
            current_value=current_value,
            reinvested=member.reinvested,
            account_balance=member.account_balance,
            pay_out=member.pay_out,
            disbursed=member.disbursed,
            last_dividend_year=member.last_dividend_year,
            issued_dividend=member.issued_dividend,
        )
        update_economics(db, member.id, member_economics_request)

    return db.query(Share).filter(Share.id == share_id).first()


def delete_share(db: Session, share_id: int):
    share = get_share(db, share_id)
    if share and share["data"]:
        member_id = share["data"][0].member_id
    else:
        return False

    deleted = db.query(Share).filter(Share.id == share_id).delete()
    if deleted != 1:
        return False

    member = get_economics_by_member(db, member_id)
    if not member or not member["data"][0]:
        return False

    economics_update = EconomicsUpdateRequest(
        nr_of_shares=member["data"][0].nr_of_shares - 1,
        total_investment=member["data"][0].total_investment - share["data"][0].initial_value,
        current_value=member["data"][0].current_value - share["data"][0].current_value,
        reinvested=member["data"][0].reinvested,
        account_balance=member["data"][0].account_balance,
        pay_out=member["data"][0].pay_out,
        disbursed=member["data"][0].disbursed,
    )

    db.query(Economics).filter(Economics.id == member["data"][0].id).update(economics_update.model_dump())

    try:
        db.commit()
    except Exception as ex:
        db.rollback()
        error_request = ErrorLogCreateRequest(
            share_id=share_id,
            member_id=member_id,
            comment=f"Error: no deleting of share {share_id}, details: {ex}",
            resolved=False,
        )
        create_error(db, error_request)
        return False

    try:
        last_item = db.query(Share).order_by(Share.id.desc()).first()
        alter_sequence_query = f"ALTER SEQUENCE shares_id_seq RESTART WITH {last_item.id + 1}"
        db.execute(text(alter_sequence_query))
        db.commit()
    except Exception as ex:
        error_request = ErrorLogCreateRequest(
            share_id=share_id,
            member_id=member_id,
            comment=f"Error resetting share sequence after deletion of share {share_id}, details: {ex}",
            resolved=False,
        )
        create_error(db, error_request)

    return share["data"][0]
