# pylint: disable=singleton-comparison

from sqlalchemy.orm import Session

from solarpark.models.shares import ShareCreateRequest
from solarpark.persistence.models.shares import Share


def get_share(db: Session, share_id: int):
    return db.query(Share).filter(Share.id == share_id).first()


def get_shares_by_member(db: Session, member_id: int):
    return db.query(Share).filter(Share.member_id == member_id).all()


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


def create_share(db: Session, share_request: ShareCreateRequest):
    share = Share(
        id=share_request.id, member_id=share_request.member_id, date=share_request.date, comment=share_request.comment
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share
