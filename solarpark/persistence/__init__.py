# pylint: disable=R0914,R0915,W0127, R0912

from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from structlog import get_logger

from solarpark.models.dividends import DividendUpdateRequest
from solarpark.models.economics import EconomicsUpdateRequest
from solarpark.models.error_log import ErrorLogCreateRequest
from solarpark.models.shares import ShareUpdateRequest
from solarpark.persistence.economics import get_all_economics_dividend
from solarpark.persistence.error_log import create_error
from solarpark.persistence.models.dividends import Dividend
from solarpark.persistence.models.economics import Economics
from solarpark.persistence.models.members import Member
from solarpark.persistence.models.payments import Payment
from solarpark.persistence.models.shares import Share
from solarpark.persistence.shares import get_shares_by_member, get_shares_by_member_and_purchase_year
from solarpark.settings import settings


def make_dividend(
    db: Session, amount: float, payment_year: int, nr_of_economics: int, is_historical_fulfillment: bool = False
):
    engine = create_engine(f"{settings.CONNECTIONSTRING_DB}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_error = SessionLocal()

    batch_size = settings.ECONOMICS_BACKGROUND_BATCH
    for i in range(0, nr_of_economics, batch_size):
        members_economics = get_all_economics_dividend(db, payment_year, range=[i, batch_size])

        if not members_economics or not members_economics["data"]:
            error_request = ErrorLogCreateRequest(
                comment=f"Error: no dividends done for members in batch {i}",
                resolved=False,
            )
            create_error(db_error, error_request)
            continue

        for member in members_economics["data"]:
            if is_historical_fulfillment:
                shares = get_shares_by_member_and_purchase_year(db, member.member_id, payment_year)
            else:
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
                    from_internal_account=share.from_internal_account,
                )

                db.query(Share).filter(Share.id == share.id).update(share_update.model_dump())
                db.flush()

            nr_of_shares = shares["total"]
            total_investment = sum(share.initial_value for share in shares["data"])
            current_value = sum(share.current_value for share in shares["data"])
            dividend = amount * sum(1 for share in shares["data"] if share.purchased_at.year < payment_year)

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
                last_dividend_year=payment_year,
                issued_dividend=datetime.now(),
            )

            db.query(Economics).filter(Economics.id == member.id).update(economics_update.model_dump())
            db.flush()

            # Should we reinvest and create new shares or not
            nr_reinvest_shares = int(member.account_balance // settings.SHARE_PRICE)
            total_investment = total_investment + nr_reinvest_shares * settings.SHARE_PRICE
            current_value = current_value + nr_reinvest_shares * settings.SHARE_PRICE
            account_balance = account_balance - nr_reinvest_shares * settings.SHARE_PRICE
            disbursed = disbursed
            reinvested = reinvested + nr_reinvest_shares * settings.SHARE_PRICE

            if not is_historical_fulfillment and nr_reinvest_shares > 0:
                nr_of_shares = nr_of_shares + nr_reinvest_shares
                for _ in range(nr_reinvest_shares):
                    share = Share(
                        member_id=member.member_id,
                        initial_value=settings.SHARE_PRICE,
                        current_value=settings.SHARE_PRICE,
                        purchased_at=date((datetime.now().year - 1), 12, 31),
                        from_internal_account=True,
                    )
                    db.add(share)
                    db.flush()

                economics_update = EconomicsUpdateRequest(
                    nr_of_shares=nr_of_shares,
                    total_investment=total_investment,
                    current_value=current_value,
                    reinvested=reinvested,
                    account_balance=account_balance,
                    pay_out=member.pay_out,
                    disbursed=disbursed,
                    last_dividend_year=payment_year,
                    issued_dividend=datetime.now(),
                )

                db.query(Economics).filter(Economics.id == member.id).update(economics_update.model_dump())
                db.flush()

            # Handle case for import of historic data
            if is_historical_fulfillment:
                economics_update = EconomicsUpdateRequest(
                    nr_of_shares=nr_of_shares,
                    total_investment=total_investment,
                    current_value=current_value,
                    reinvested=reinvested,
                    account_balance=account_balance,
                    pay_out=member.pay_out,
                    disbursed=disbursed,
                    last_dividend_year=payment_year,
                    issued_dividend=datetime.now(),
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

    dividend_update = DividendUpdateRequest(dividend_per_share=amount, payment_year=payment_year, completed=True)
    db.query(Dividend).filter(Dividend.payment_year == payment_year).update(dividend_update.model_dump())
    db.commit()

    db_error.close()
    get_logger().info(f"fulfilled dividend {payment_year} successfully")


def delete_all_member_data(db: Session, member_id: int):
    engine = create_engine(f"{settings.CONNECTIONSTRING_DB}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_error = SessionLocal()

    member = db.query(Member).filter(Member.id == member_id).first()

    db.query(Share).filter(Share.member_id == member_id).delete()
    db.query(Economics).filter(Economics.member_id == member_id).delete()
    db.query(Member).filter(Member.id == member_id).delete()

    try:
        db.commit()
        return member
    except Exception as ex:
        db.rollback()
        error_request = ErrorLogCreateRequest(
            member_id=member_id,
            comment=f"Error: no member deleted: {ex}",
            resolved=False,
        )
        create_error(db_error, error_request)
        return False
