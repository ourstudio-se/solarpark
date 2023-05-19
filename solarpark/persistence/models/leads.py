from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from solarpark.persistence.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    birth_date = Column(Integer, nullable=True)
    company_name = Column(String, nullable=True)
    org_number = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    existing_id = Column(Integer, nullable=True)
    quantity_shares = Column(Integer, nullable=True)
    generate_certificate = Column(Boolean, nullable=True)