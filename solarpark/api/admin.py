import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.models.economics import EconomicsCreateRequest
from solarpark.models.members import MemberCreateRequest
from solarpark.models.shares import ShareCreateRequestImport
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import create_economics, get_economics_by_member
from solarpark.persistence.members import count_all_members, create_member, get_all_members
from solarpark.persistence.shares import create_share_import, get_shares_by_member
from solarpark.settings import settings

router = APIRouter()


def parse_birth_date(birth_date: str):
    if len(birth_date) == 8 and (birth_date.startswith("19") or birth_date.startswith("20")):
        return datetime.strptime(birth_date, "%Y%m%d")
    if len(birth_date) == 4:
        return datetime.strptime(birth_date, "%Y")
    if len(birth_date) == 6:
        return datetime.strptime(birth_date, "%y%m%d")
    if len(birth_date) == 10:
        return datetime.strptime(birth_date[:6], "%y%m%d")
    if len(birth_date) == 12:
        return datetime.strptime(birth_date[:8], "%Y%m%d")

    return None


def create_economics_for_all_members(db: Session):
    """Create economics for existing members with shares"""
    member_count = count_all_members(db)
    offset = 0
    limit = 20

    while offset < member_count:
        members = get_all_members(db, [], [offset, limit])

        if not members and "data" not in members:
            get_logger().error("error fetching members, aborting job")
            break

        for member in members["data"]:
            # Iterate members and check if they have economics record already created
            member_economics = get_economics_by_member(db=db, member_id=member.id)

            if member_economics and "data" in member_economics and member_economics["total"] == 0:
                # Get member shares and skip member if no shares found
                member_shares = get_shares_by_member(db, member_id=member.id)

                if member_shares and "data" in member_shares and member_shares["total"] > 0:
                    # Create economics record for member
                    nr_of_shares = member_shares["total"]
                    total_investment = sum(share.initial_value for share in member_shares["data"])
                    current_value = sum(share.current_value for share in member_shares["data"])

                    created = create_economics(
                        db,
                        EconomicsCreateRequest(
                            member_id=member.id,
                            nr_of_shares=nr_of_shares,
                            total_investment=total_investment,
                            current_value=current_value,
                            account_balance=0,
                            reinvested=0,
                            pay_out=False,
                        ),
                    )

                    if created:
                        get_logger().info(f"created economics record successfully for member {member.id}")
                    else:
                        get_logger().error(f"error creating economics record for member {member.id}")

        # Increment offset for next batch
        offset += limit


@router.post("/import-members", summary="Import members from csv", status_code=202)
async def import_members(
    member_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    Upload CSV-file with members
    """

    def member_logic(db: Session, dict_reader: csv.DictReader):
        errors = []
        for row in dict_reader:
            try:
                if len(row) == 18:
                    if "-" in row["Födelsedatum"] or len(row["Födelsedatum"]) > 8:
                        # Organization member
                        new_member = MemberCreateRequest(
                            id=row["Medlemnr"],
                            year=datetime.strptime(row["År"].strip(), "%Y"),
                            org_name=row["Efternamn/Företagsnamn"].strip(),
                            org_number=row["Födelsedatum"].strip(),
                            street_address=row["Gatuadress"].strip(),
                            zip_code=str(row["Postnr."].replace(" ", "")),
                            telephone=row["Telefonnr."].replace("-", ""),
                            email=row["Mailadress"].strip(),
                            bank=row["Bank"].strip(),
                            swish=row["Swish"].strip().replace("-", ""),
                        )
                    else:
                        # Private person member
                        new_member = MemberCreateRequest(
                            id=row["Medlemnr"],
                            year=datetime.strptime(row["År"].strip(), "%Y"),
                            firstname=row["Förnamn"].strip(),
                            lastname=row["Efternamn/Företagsnamn"].strip() if row["Efternamn/Företagsnamn"] else None,
                            birth_date=parse_birth_date(row["Födelsedatum"].strip()),
                            street_address=row["Gatuadress"].strip(),
                            zip_code=str(row["Postnr."].replace(" ", "")) if row["Postnr."] else None,
                            telephone=row["Telefonnr."].strip().replace("-", ""),
                            email=row["Mailadress"].strip(),
                            bank=row["Bank"].strip(),
                            swish=row["Swish"].strip().replace("-", ""),
                        )

                    create_member(db, new_member)
                else:
                    get_logger().error(f"expected 18 columns per row, found {len(row)}, skipping row..")
            except Exception as ex:
                get_logger().error(f"error creating member {row['Medlemnr']}, details: {ex}")
                errors.append(row["Medlemnr"])
                continue

        if errors:
            get_logger().error(f"{len(errors)} members could not be imported, {errors}")

    reader = None
    try:
        contents = member_file.file.read()
        buffer = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
        if reader:
            background_tasks.add_task(member_logic, db, reader)
    except Exception as ex:
        get_logger().error(f"error reading csv-file: {ex}")
        raise HTTPException(status_code=400, detail="error reading csv file, see logs for more info") from ex


@router.post("/import-shares", summary="Import shares from csv", status_code=202)
async def get_analytics_endpoint(
    share_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    Upload CSV-file with member shares
    """

    def share_logic(db: Session, dict_reader: csv.DictReader):
        errors = []
        for row in dict_reader:
            try:
                if len(row) == 12 or len(row) == 13:
                    new_share = ShareCreateRequestImport(
                        id=row["Andel nr"],
                        member_id=row["Medlem"],
                        purchased_at=datetime.strptime(row["Datum"].strip(), "%y%m%d"),
                        comment=row["Amn."].strip(),
                        initial_value=settings.SHARE_PRICE,
                        current_value=settings.SHARE_PRICE,
                        from_internal_account=False,
                    )

                    create_share_import(db, new_share)
                else:
                    get_logger().error(f"expected 18 columns per row, found {len(row)}, skipping row..")
            except Exception as ex:
                get_logger().error(f"error creating share {row['Andel nr']}, details: {ex}")
                errors.append(row["Andel nr"])
                continue

        if errors:
            get_logger().error(f"{len(errors)} shares could not be imported, {errors}")

    reader = None
    try:
        contents = share_file.file.read()
        buffer = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
        if reader:
            background_tasks.add_task(share_logic, db, reader)
    except Exception as ex:
        get_logger().error(f"error reading csv-file: {ex}")
        raise HTTPException(status_code=400, detail="error reading csv file, see logs for more info") from ex


@router.post(
    "/create-economics-for-members",
    summary="Create economics for all members after import",
    status_code=202,
)
async def create_economics_endpoint(
    background_tasks: BackgroundTasks = BackgroundTasks(), db: Session = Depends(get_db)
):
    """
    Creates economics records for all members as background job.
    This endpoint is generally called once after initial import.
    Can be called multiple times without issues.
    """
    background_tasks.add_task(create_economics_for_all_members, db)
