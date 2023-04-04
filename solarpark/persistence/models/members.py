from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from solarpark.persistence.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    org_name = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    birth_date = Column(Integer, nullable=True)
    org_number = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    bank = Column(String, nullable=True)
    swish = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
