from sqlalchemy import Column, DateTime, Integer, String, func

from solarpark.persistence.database import Base


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
    year = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
