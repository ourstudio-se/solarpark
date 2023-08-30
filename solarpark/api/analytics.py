from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.economics import get_total_account_balance, get_total_disbursed
from solarpark.persistence.error_log import get_all_unresolved_errors
from solarpark.persistence.members import count_all_members
from solarpark.persistence.payments import get_year_payments
from solarpark.persistence.shares import count_all_shares
from solarpark.settings import settings

router = APIRouter()


def format_numbers(x):
    """
    Makes 1000 -> 1 000

    """
    return f"{x:_}".replace("_", " ")


@router.get("/analytics", summary="Get analytical data")
async def get_analytics_endpoint(db: Session = Depends(get_db)):
    all_members = count_all_members(db, filter_on_org=False)
    all_member_organizations = count_all_members(db, filter_on_org=True)
    all_shares, reinvested_shares, org_more_than_one_share = count_all_shares(db)
    total_account_balance = get_total_account_balance(db)
    total_disbursed = get_total_disbursed(db)
    year_payments = get_year_payments(db)
    errors = get_all_unresolved_errors(db)

    return {
        "errors": {"unresolved_errors": format_numbers(errors)},
        "members": {
            "total_count": format_numbers(all_members),
            "private_persons": format_numbers(all_members - all_member_organizations),
            "organizations": format_numbers(all_member_organizations),
        },
        "shares": {
            "total_count": format_numbers(all_shares),
            "reinvested_count": format_numbers(reinvested_shares),
            "org_more_than_one_share": format_numbers(org_more_than_one_share),
            "average_share_count_per_member": format_numbers(round(all_shares / all_members)),
        },
        "economics": {
            "total_value": format_numbers(all_shares * settings.SHARE_PRICE),
            "reinvested_value": format_numbers(reinvested_shares * settings.SHARE_PRICE),
            "total_account_balance": format_numbers(total_account_balance),
        },
        "payments": {
            "total_disbursed": format_numbers(total_disbursed),
            "year_payments": format_numbers(year_payments),
        },
    }
