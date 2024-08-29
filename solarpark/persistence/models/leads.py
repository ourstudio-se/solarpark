from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from solarpark.persistence.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto", nullable=False)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    org_name = Column(String, nullable=True)
    org_number = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    email = Column(String, nullable=False)
    telephone = Column(String, nullable=True)
    existing_id = Column(Integer, nullable=True)
    quantity_shares = Column(Integer, nullable=False)
    generate_certificate = Column(Boolean, nullable=True)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
