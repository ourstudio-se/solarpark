# pylint: disable=R0914,R0915,W0127

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from solarpark.models.economics import EconomicsUpdateRequest
from solarpark.models.error_log import ErrorLogCreateRequest
from solarpark.models.shares import ShareUpdateRequest
from solarpark.persistence.economics import get_all_economics
from solarpark.persistence.error_log import create_error
from solarpark.persistence.models.economics import Economics
from solarpark.persistence.models.payments import Payment
from solarpark.persistence.models.shares import Share
from solarpark.persistence.shares import get_shares_by_member
from solarpark.settings import settings


def make_dividend(db: Session, amount: float, payment_year: int, nr_of_economics: int):
    engine = create_engine(f"{settings.CONNECTIONSTRING_DB}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_error = SessionLocal()

    batch_size = settings.ECONOMICS_BACKGROUND_BATCH
    for i in range(0, nr_of_economics, batch_size):
        members_economics = get_all_economics(db, sort=[], range=[i, batch_size])

        if not members_economics or not members_economics["data"]:
            error_request = ErrorLogCreateRequest(
                comment=f"Error: no dividends done for members in batch {i}",
                resolved=False,
            )
            create_error(db_error, error_request)
            continue

        for member in members_economics["data"]:
            shares = get_shares_by_member(db, member.member_id)

            if not shares["total"] or not shares["data"]:
                error_request = ErrorLogCreateRequest(
                    member_id=member.member_id,
                    comment="Error: no shares found, no dividends done",
                    resolved=False,
                )
                create_error(db_error, error_request)
                continue

            for share in shares["data"]:
                if share.purchased_at.year >= payment_year:
                    continue

                current_value = max(share.current_value - amount, 0)

                share_update = ShareUpdateRequest(
                    comment=share.comment,
                    purchased_at=share.purchased_at,
                    member_id=share.member_id,
                    initial_value=share.initial_value,
                    current_value=current_value,
                )

                db.query(Share).filter(Share.id == share.id).update(share_update.model_dump())
                db.flush()

            nr_of_shares = shares["total"]
            total_investment = sum(share.initial_value for share in shares["data"])
            current_value = sum(share.current_value for share in shares["data"])
            dividend = amount * nr_of_shares

            account_balance = dividend + member.account_balance
            disbursed = member.disbursed
            reinvested = member.reinvested

            if member.pay_out:
                disbursed = dividend + disbursed + member.account_balance
                account_balance = 0

                payment = Payment(
                    member_id=member.member_id,
                    year=datetime.now().year,
                    amount=(dividend + member.account_balance),
                    paid_out=False,
                )
                db.add(payment)
                db.flush()

            economics_update = EconomicsUpdateRequest(
                nr_of_shares=nr_of_shares,
                total_investment=total_investment,
                current_value=current_value,
                reinvested=reinvested,
                account_balance=account_balance,
                pay_out=member.pay_out,
                disbursed=disbursed,
            )

            db.query(Economics).filter(Economics.id == member.id).update(economics_update.model_dump())
            db.flush()

            nr_reinvest_shares = int(member.account_balance // settings.SHARE_PRICE)
            if nr_reinvest_shares > 0:
                for _ in range(nr_reinvest_shares):
                    share = Share(
                        comment="From internal account",
                        member_id=member.member_id,
                        initial_value=settings.SHARE_PRICE,
                        current_value=settings.SHARE_PRICE,
                        purchased_at=datetime.now(),
                    )
                    db.add(share)
                    db.flush()

                nr_of_shares = nr_of_shares + nr_reinvest_shares
                total_investment = total_investment + nr_reinvest_shares * settings.SHARE_PRICE
                current_value = current_value + nr_reinvest_shares * settings.SHARE_PRICE
                account_balance = account_balance - nr_reinvest_shares * settings.SHARE_PRICE
                disbursed = disbursed
                reinvested = reinvested + nr_reinvest_shares * settings.SHARE_PRICE

                economics_update = EconomicsUpdateRequest(
                    nr_of_shares=nr_of_shares,
                    total_investment=total_investment,
                    current_value=current_value,
                    reinvested=reinvested,
                    account_balance=account_balance,
                    pay_out=member.pay_out,
                    disbursed=disbursed,
                )

                db.query(Economics).filter(Economics.id == member.id).update(economics_update.model_dump())
                db.flush()

            try:
                db.commit()
            except Exception as ex:
                db.rollback()
                error_request = ErrorLogCreateRequest(
                    member_id=member.member_id,
                    comment=f"Error: no dividend done, details: {ex}",
                    resolved=False,
                )
                create_error(db_error, error_request)

    db_error.close()
    print("Done!")
