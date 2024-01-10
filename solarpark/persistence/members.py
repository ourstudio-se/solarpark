# pylint: disable=singleton-comparison,W0622
from typing import Dict, List

from sqlalchemy import and_, text
from sqlalchemy.orm import Session

from solarpark.models.members import MemberCreateRequest, MemberUpdateRequest
from solarpark.persistence.models.members import Member


def find_member(db: Session, term: str):
    split_term = term.split(" ")

    if len(split_term) == 2:
        result = (
            db.query(Member)
            .filter(and_(Member.firstname.ilike(f"%{split_term[0]}%"), Member.lastname.ilike(f"%{split_term[1]}%")))
            .all()
        )
    else:
        result = (
            db.query(Member)
            .filter(
                Member.firstname.ilike(f"%{term}%")
                | Member.lastname.ilike(f"%{term}%")
                | Member.org_name.ilike(f"%{term}%")
                | Member.email.ilike(f"%{term}%")
            )
            .all()
        )
    return {"data": result, "total": len(result)}


def get_member(db: Session, member_id: int):
    result = db.query(Member).filter(Member.id == member_id).all()
    return {"data": result, "total": len(result)}


def get_member_by_list_ids(db: Session, member_ids: list):
    result = db.query(Member).filter(Member.id.in_(member_ids)).all()
    return {"data": result, "total": len(result)}


def get_all_members(db: Session, sort: List, range: List) -> Dict:
    total_count = db.query(Member).count()

    # Pagination and sort order
    if len(range) == 2 and len(sort) == 2:
        return {
            "data": db.query(Member)
            .order_by(text(f"{sort[0]} {sort[1].lower()}"))
            .offset(range[0])
            .limit(range[1])
            .all(),
            "total": total_count,
        }

    # Pagination only
    if len(range) == 2:
        return {
            "data": db.query(Member).order_by(Member.id).offset(range[0]).limit(range[1]).all(),
            "total": total_count,
        }
    # "data": db.query(Member).order_by(Member.id).offset(0).limit(10).all()
    return {
        "data": db.query(Member).order_by(Member.id).offset(0).limit(10).all(),
        "total": total_count,
    }


def count_all_members(db: Session, filter_on_org: bool = False):
    if filter_on_org:
        return db.query(Member).filter(Member.org_number != None).count()  # noqa: E711
    return db.query(Member).count()


def update_member(db: Session, member_id: int, member_update: MemberUpdateRequest):
    db.query(Member).filter(Member.id == member_id).update(member_update.model_dump())
    db.commit()
    return db.query(Member).filter(Member.id == member_id).first()


def delete_member(db: Session, member_id: int) -> bool:
    deleted = db.query(Member).filter(Member.id == member_id).delete()
    if deleted == 1:
        db.commit()
        return True
    return False


def create_member(db: Session, member_request: MemberCreateRequest):
    member = Member(
        firstname=member_request.firstname,
        lastname=member_request.lastname,
        org_name=member_request.org_name,
        org_number=member_request.org_number,
        year=member_request.year,
        birth_date=member_request.birth_date,
        street_address=member_request.street_address,
        zip_code=member_request.zip_code,
        telephone=member_request.telephone,
        email=member_request.email,
        bank=member_request.bank,
        swish=member_request.swish,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
