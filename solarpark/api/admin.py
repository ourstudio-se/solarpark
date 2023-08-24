import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.models.members import MemberCreateRequest
from solarpark.models.shares import ShareCreateRequestImport
from solarpark.persistence.database import get_db
from solarpark.persistence.members import create_member
from solarpark.persistence.shares import create_share_import
from solarpark.settings import settings

router = APIRouter()


def parse_birth_date(birth_date: str):
    if len(birth_date) == 8 and (birth_date.startswith("19") or birth_date.startswith("20")):
        return datetime.strptime(birth_date, "%Y%m%d")
    if len(birth_date) == 4:
        return datetime.strptime(birth_date, "%Y")
    return None


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
                    new_share = ShareCreateRequestImport(
                        id=row["Andel nr"],
                        member_id=row["Medlem"],
                        purchased_at=datetime.strptime(row["Datum"].strip(), "%y%m%d"),
                        comment=row["Amn."].strip(),
                        initial_value=settings.SHARE_PRICE,
                        current_value=row["Andelsvärde"] if row["Andelsvärde"] else settings.SHARE_PRICE,
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
