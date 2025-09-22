# pylint: disable=R0914,R0915,W0127, R0912,C0301

from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.models.dividends import DividendUpdateRequest
from solarpark.models.economics import EconomicsUpdateRequest
from solarpark.models.error_log import ErrorLogCreateRequest
from solarpark.models.shares import ShareUpdateRequest
from solarpark.persistence.database import SessionLocal
from solarpark.persistence.economics import get_all_economics_dividend
from solarpark.persistence.error_log import create_error
from solarpark.persistence.models.dividends import Dividend
from solarpark.persistence.models.economics import Economics
from solarpark.persistence.models.members import Member
from solarpark.persistence.models.payments import Payment
from solarpark.persistence.models.shares import Share
from solarpark.persistence.shares import get_shares_by_member
from solarpark.settings import settings


def make_dividend(amount: float, payment_year: int, nr_of_economics: int, is_historical_fulfillment: bool = False):
    db: Session = SessionLocal()
    try:
        batch_size = settings.ECONOMICS_BACKGROUND_BATCH
        for i in range(0, nr_of_economics, batch_size):

            members_economics_batch = get_all_economics_dividend(db, range=[i, batch_size])
            if not members_economics_batch or not members_economics_batch["data"]:
                error_request = ErrorLogCreateRequest(
                    comment=f"Error: no dividends done for members in batch {i}, {members_economics_batch['data']}, {members_economics_batch}",
                    resolved=False,
                )
                create_error(db, error_request)

                continue

            for member_economics in members_economics_batch["data"]:
                if member_economics.last_dividend_year >= payment_year:
                    get_logger().info(
                        f"Skipping member {member_economics.member_id}, dividend already done for year {payment_year}"
                    )

                    continue

                shares = get_shares_by_member(db, member_economics.member_id)
                if not shares["total"] or not shares["data"]:
                    error_request = ErrorLogCreateRequest(
                        member_id=member_economics.member_id,
                        comment="Error: no shares found, no dividends done",
                        resolved=False,
                    )
                    create_error(db, error_request)

                    continue

                current_nr_of_shares = shares["total"]
                current_disbursed = member_economics.disbursed
                current_reinvested = member_economics.reinvested
                current_total_investment = sum(share.initial_value for share in shares["data"])

                new_dividend = amount * sum(1 for share in shares["data"] if share.purchased_at.year < payment_year)
                new_account_balance = new_dividend + member_economics.account_balance

                new_disbursed = current_disbursed
                if member_economics.pay_out:
                    new_disbursed = current_disbursed + new_account_balance

                    payment = Payment(
                        member_id=member_economics.member_id,
                        year=payment_year
                        + 1,  # datetime.now().year, # ÄNDARA HÄR OCH KÖR OM JUST NU och ta bort sen fwemfoiawemfioawefoå
                        amount=new_account_balance,
                        paid_out=False,
                    )

                    new_account_balance = 0
                    db.add(payment)

                nr_of_shares_to_reinvest = int(new_account_balance // settings.SHARE_PRICE)
                new_account_balance_after_reinvestment = (
                    new_account_balance - nr_of_shares_to_reinvest * settings.SHARE_PRICE
                )
                new_current_reinvested = current_reinvested + nr_of_shares_to_reinvest * settings.SHARE_PRICE
                new_total_investment = current_total_investment + nr_of_shares_to_reinvest * settings.SHARE_PRICE

                new_total_current_value_of_share = update_shares_for_dividend(db, shares, payment_year, amount)
                new_total_current_value_of_shares_with_reinvested_shares = (
                    new_total_current_value_of_share + nr_of_shares_to_reinvest * settings.SHARE_PRICE
                )

                economics_update = EconomicsUpdateRequest(
                    nr_of_shares=current_nr_of_shares + nr_of_shares_to_reinvest,
                    total_investment=new_total_investment,
                    current_value=new_total_current_value_of_shares_with_reinvested_shares,
                    reinvested=new_current_reinvested,
                    account_balance=new_account_balance_after_reinvestment,
                    pay_out=member_economics.pay_out,
                    disbursed=new_disbursed,
                    last_dividend_year=payment_year,
                    issued_dividend=datetime.now(timezone.utc),
                )

                db.query(Economics).filter(Economics.id == member_economics.id).update(economics_update.model_dump())

                if not is_historical_fulfillment and nr_of_shares_to_reinvest > 0:
                    for _ in range(nr_of_shares_to_reinvest):
                        share = Share(
                            member_id=member_economics.member_id,
                            initial_value=settings.SHARE_PRICE,
                            current_value=settings.SHARE_PRICE,
                            purchased_at=date((payment_year), 12, 31),  # date((datetime.now().year - 1), 12, 31),
                            from_internal_account=True,
                        )
                        db.add(share)

                try:
                    db.commit()
                    get_logger().info(f"committed dividend for member {member_economics.member_id} successfully")
                except Exception as ex:
                    db.rollback()
                    get_logger().error(
                        f"failed to commit dividend for member {member_economics.member_id}, details: {ex}"
                    )
                    error_request = ErrorLogCreateRequest(
                        member_id=member_economics.member_id,
                        comment=f"Error: no dividend done, details: {ex}",
                        resolved=False,
                    )
                    create_error(db, error_request)

        dividend_update = DividendUpdateRequest(dividend_per_share=amount, payment_year=payment_year, completed=True)
        db.query(Dividend).filter(Dividend.payment_year == payment_year).update(dividend_update.model_dump())
        db.commit()
        get_logger().info(f"fulfilled dividend {payment_year} successfully")

    finally:
        db.close()


def update_shares_for_dividend(db: Session, shares, payment_year: int, amount: float) -> int:
    new_total_current_value_of_share = 0
    for share in shares["data"]:
        if share.purchased_at.year >= payment_year:
            new_total_current_value_of_share += share.current_value
            continue

        new_current_value = max(share.current_value - amount, 0)
        new_total_current_value_of_share += new_current_value

        share_update = ShareUpdateRequest(
            comment=share.comment,
            purchased_at=share.purchased_at,
            member_id=share.member_id,
            initial_value=share.initial_value,
            current_value=new_current_value,
            from_internal_account=share.from_internal_account,
        )
        db.query(Share).filter(Share.id == share.id).update(share_update.model_dump())

    return new_total_current_value_of_share


def delete_all_member_data(db: Session, member_id: int):

    member = db.query(Member).filter(Member.id == member_id).first()

    db.query(Share).filter(Share.member_id == member_id).delete()
    db.query(Economics).filter(Economics.member_id == member_id).delete()
    db.query(Member).filter(Member.id == member_id).delete()

    try:
        db.commit()
    except Exception as ex:
        db.rollback()
        error_request = ErrorLogCreateRequest(
            member_id=member_id,
            comment=f"Error: no member deleted: {ex}",
            resolved=False,
        )
        create_error(db, error_request)
        return False

    try:
        last_item = db.query(Member).order_by(Member.id.desc()).first()
        alter_sequence_query = f"ALTER SEQUENCE members_id_seq RESTART WITH {last_item.id + 1}"
        db.execute(text(alter_sequence_query))
        db.commit()
    except Exception as ex:
        db.rollback()
        error_request = ErrorLogCreateRequest(
            member_id=member_id,
            comment=f"Error resetting member sequence after deletion of member {member_id}, details: {ex}",
            resolved=False,
        )
        create_error(db, error_request)

    return member
