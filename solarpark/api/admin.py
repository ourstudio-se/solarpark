import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.models.members import MemberCreateRequest
from solarpark.models.shares import ShareCreateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.members import create_member
from solarpark.persistence.shares import create_share

router = APIRouter()


@router.post("/import-members", summary="Import members from csv")
async def import_members(member_file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV-file with members
    """
    reader = None
    try:
        contents = member_file.file.read()
        buffer = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
    except Exception as ex:
        get_logger().error(f"error reading csv-file: {ex}")

    errors = []
    if reader:
        for row in reader:
            try:
                if len(row) == 18:
                    if "-" in row["Födelsedatum"] or len(row["Födelsedatum"]) == 10:
                        # Organization member
                        new_member = MemberCreateRequest(
                            id=row["Medlemnr"],
                            year=row["År"].strip(),
                            org_name=row["Efternamn/Företagsnamn"].strip(),
                            org_number=row["Födelsedatum"].strip(),
                            street_address=row["Gatuadress"].strip(),
                            zip_code=row["Postnr."].replace(" ", ""),
                            telephone=row["Telefonnr."],
                            email=row["Mailadress"].strip(),
                            bank=row["Bank"].strip(),
                            swish=row["Swish"].strip(),
                        )
                    else:
                        # Private person member
                        new_member = MemberCreateRequest(
                            id=row["Medlemnr"],
                            year=row["År"].strip(),
                            firstname=row["Förnamn"].strip(),
                            lastname=row["Efternamn/Företagsnamn"].strip()
                            if row["Efternamn/Företagsnamn"]
                            else "Saknas",
                            birth_date=row["Födelsedatum"].strip() if row["Födelsedatum"] else 0000,
                            street_address=row["Gatuadress"].strip(),
                            zip_code=row["Postnr."].replace(" ", "") if row["Postnr."] else 0,
                            telephone=row["Telefonnr."].strip(),
                            email=row["Mailadress"].strip(),
                            bank=row["Bank"].strip(),
                            swish=row["Swish"].strip(),
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


@router.post("/import-shares", summary="Import shares from csv")
async def get_analytics_endpoint(share_file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV-file with member shares
    """

    reader = None
    try:
        contents = share_file.file.read()
        buffer = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
    except Exception as ex:
        get_logger().error(f"error reading csv-file: {ex}")

    errors = []
    if reader:
        for row in reader:
            try:
                if len(row) == 12:
                    new_share = ShareCreateRequest(
                        id=row["Andel nr"],
                        member_id=row["Medlem"],
                        date=row["Datum"],
                        comment=row["Amn."],
                        initial_value=3000,
                        current_value=row["Andelsvärde"] if row["Andelsvärde"] else 3000,
                    )

                    create_share(db, new_share)
                else:
                    get_logger().error(f"expected 18 columns per row, found {len(row)}, skipping row..")
            except Exception as ex:
                get_logger().error(f"error creating share {row['Andel nr']}, details: {ex}")
                errors.append(row["Andel nr"])
                continue

    if errors:
        get_logger().error(f"{len(errors)} shares could not be imported, {errors}")
