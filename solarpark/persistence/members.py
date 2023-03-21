from sqlalchemy.orm import Session

from solarpark.models.members import MemberCreateRequest, MemberUpdateRequest
from solarpark.persistence.models.members import Member


def find_member(db: Session, term: str):
    return db.query(Member).filter(Member.firstname.ilike(f"%{term}%") | Member.lastname.ilike(f"%{term}%")).all()


def get_member(db: Session, member_id: int):
    return db.query(Member).filter(Member.id == member_id).first()


def get_all_members(db: Session):
    return db.query(Member).all()


def count_all_members(db: Session, filter_on_org: bool = False):
    if filter_on_org:
        return db.query(Member).filter(Member.org_number is not None).count()
    return db.query(Member).count()


def update_member(db: Session, member_id: int, member_update: MemberUpdateRequest):
    db.query(Member).filter(Member.id == member_id).update(member_update.dict())
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
        id=member_request.id,
        firstname=member_request.firstname,
        lastname=member_request.lastname,
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
