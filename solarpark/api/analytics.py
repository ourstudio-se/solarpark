from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.members import count_all_members
from solarpark.persistence.shares import count_all_shares
from solarpark.settings import settings

router = APIRouter()


@router.get("/analytics", summary="Get analytical data")
async def get_analytics_endpoint(db: Session = Depends(get_db)):
    """
    1. totalt antal medlemmar som äger andelar          # KLAR
    2. Totalt antal företag som äger andelar            # KLAR
    3. Totalt antal företag med fler än 1 andel
    4. totalt antal andelar                             # KLAR
    5. summa instats (andelar * 3000) (kr)              # KLAR
    6. totalt utdelat/återbetalat (kr)
    7. Totalt utbetalt för året (kr)
    8. Totalt värde konton (kr)
    9. totalt kontoköp (kr)?


    """
    all_members = count_all_members(db, filter_on_org=False)
    all_member_organizations = count_all_members(db, filter_on_org=True)
    all_shares = count_all_shares(db)

    return {
        "members": {
            "total_count": all_members,
            "private_persons": all_members - all_member_organizations,
            "organizations": all_member_organizations,
        },
        "shares": {
            "total_count": all_shares,
            "total_value": all_shares * settings.SHARE_PRICE,
            "average_share_count_per_member": all_shares / all_members,
        },
    }
