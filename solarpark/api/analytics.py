from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.economics import get_total_account_balance, get_total_disbursed
from solarpark.persistence.error_log import get_all_unresolved_errors
from solarpark.persistence.leads import count_all_leads
from solarpark.persistence.payments import get_year_payments
from solarpark.persistence.shares import all_members_with_shares, count_all_shares
from solarpark.settings import settings

router = APIRouter()


@router.get("/analytics", summary="Get analytical data")
async def get_analytics_endpoint(db: Session = Depends(get_db)):
    try:
        all_members, all_member_organizations = all_members_with_shares(db)
        all_shares, all_shares_solarpark_excluded, reinvested_shares, org_more_than_one_share = count_all_shares(db)
        total_account_balance = get_total_account_balance(db)
        total_disbursed = get_total_disbursed(db)
        year_payments = get_year_payments(db)
        errors = get_all_unresolved_errors(db)
        total_leads = count_all_leads(db)

        return {
            "errors": {"unresolved_errors": errors},
            "members": {
                "total_count": all_members,
                "private_persons": all_members - all_member_organizations,
                "organizations": all_member_organizations,
            },
            "shares": {
                "total_count": all_shares,
                "total_count_solarpark_excluded": all_shares_solarpark_excluded,
                "reinvested_count": reinvested_shares,
                "org_more_than_one_share": org_more_than_one_share,
                "average_share_count_per_member": round(all_shares / all_members),
            },
            "economics": {
                "total_value": all_shares * settings.SHARE_PRICE,
                "reinvested_value": reinvested_shares * settings.SHARE_PRICE,
                "total_account_balance": total_account_balance,
            },
            "payments": {
                "total_disbursed": total_disbursed,
                "year_payments": year_payments,
            },
            "leads": {
                "total_leads": total_leads,
            },
        }
    except Exception as ex:
        raise HTTPException(status_code=400, detail="error getting analytics") from ex
