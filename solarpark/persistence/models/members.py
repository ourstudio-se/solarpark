from sqlalchemy import Column, DateTime, Integer, String

from solarpark.persistence.database import Base, utcnow


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    org_name = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    org_number = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=False)
    bank = Column(String, nullable=True)
    swish = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=utcnow())
    updated_at = Column(DateTime, onupdate=utcnow())
