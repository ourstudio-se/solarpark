from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from solarpark.persistence.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    firstname = Column(String)
    lastname = Column(String)
    year = Column(Integer)
    birth_date = Column(Integer)
    org_number = Column(String, nullable=True)
    street_address = Column(String)
    zip_code = Column(Integer)
    telephone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    bank = Column(String, nullable=True)
    swish = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
