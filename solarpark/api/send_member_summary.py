# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from solarpark.persistence.database import get_db
# from solarpark.persistence.economics import get_economics_by_member
# from solarpark.persistence.members import get_member
# from solarpark.persistence.payments import get_payment_by_member_id
# from solarpark.persistence.shares import get_shares_by_member


# router = APIRouter()

# def send_member_summary(db: Session, member_id: int):
#     members = get_member(db, member_id)
#     if len(members["data"]) > 1:
#         raise HTTPException(status_code=400, detail="member not unique")

#     if len(members["data"]) != 1:
#         raise HTTPException(status_code=400, detail="member not found")

#     shares = get_shares_by_member(db, member_id)
#     if not len(shares["data"]) > 0:
#         raise HTTPException(status_code=400, detail="no shares found for member")

#     economics = get_economics_by_member(db, member_id)
#     if not len(economics["data"]) > 0:
#         raise HTTPException(status_code=400, detail="no economics found for member")

#     members = members["data"][0]
#     shares = shares["data"]
#     economics = economics["data"]
#     payments = get_payment_by_member_id(db, member_id)
#     return {"member": members, "shares": shares, "economics": economics, "payments": payments["data"]}


# @router.post(
#     "/email/test2",
#     summary="Summation and certificate of participation for member",
#     status_code=202,
# )
# async def send_member_summary_endpoint(member_id: int, db: Session = Depends(get_db)):
#     member_summary = send_member_summary(db, member_id)
#     return member_summary
