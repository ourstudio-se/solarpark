# pylint: disable=R0914, C0200
import re
from typing import Dict

from sqlalchemy.orm import Session

from solarpark.models.leads import LeadCreateRequest
from solarpark.persistence.leads import create_lead


def commit_email_hook(db: Session, request: Dict):
    pattern_plain = "\r\n----------------------------------------\r\n|\r\n----------------------------------------\r\n"
    plain_raw = re.split(pattern_plain, request["plain"])[1].replace("\r\n", ",")  # =,
    pattern_key_value = ": |,"
    key_values = re.split(pattern_key_value, plain_raw)

    keys = []
    values = []
    for i in range(len(key_values)):
        if i % 2:
            values.append(key_values[i])
        else:
            keys.append(key_values[i])

    plain_dict = dict(zip(keys, values))
    first_last_name = re.split(" ", plain_dict["Namn"])
    quantity_shares = re.split(" ", plain_dict["Antal beställda andelar"])[0]
    generate_certificate = "Ja" == plain_dict["Andelsbevis via epost"]
    existing_id = int(plain_dict["Medlemsnummer"]) if (plain_dict["Medlemsnummer"] != "") else 0

    birth_date = (
        int(plain_dict["Personnummer"][0:-4])  # Not security number
        if len(plain_dict["Personnummer"]) > 9
        else int(plain_dict["Personnummer"])
    )
    # Behöver hantera mellannamn
    lead_request = LeadCreateRequest(
        firstname=first_last_name[0],
        lastname=first_last_name[1],
        birth_date=birth_date,
        org_name=plain_dict["Namn"],
        org_number=plain_dict["Personnummer"],
        street_address=plain_dict["Adress"],
        zip_code=plain_dict["Postnummer"],
        locality=plain_dict["Ort"],
        email=plain_dict["E-post"],
        telephone=plain_dict["Telefonnummer"],
        existing_id=existing_id,
        quantity_shares=int(quantity_shares),
        generate_certificate=generate_certificate,
    )

    return create_lead(db, lead_request)
